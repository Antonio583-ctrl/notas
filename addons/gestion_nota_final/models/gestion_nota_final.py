from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NotaFinal(models.Model):
    _name = 'gestion.nota.final'
    _description = 'Nota Final'
    _rec_name = 'student_id'
    _sql_constraints = [
        ('student_section_unique', 'unique(student_id, section_id)', 'Ya existe una nota final para este estudiante en esta sección.'),
    ]

    student_id = fields.Many2one(
        'gestion.student',
        string='Estudiante',
        ondelete='cascade',
        required=True,
    )
    section_id = fields.Many2one(
        'gestion.seccion',
        string='Sección',
        ondelete='cascade',
        required=True,
    )
    subject_id = fields.Many2one(
        'gestion.materia',
        string='Materia',
        related='section_id.subject_id',
        store=True,
        readonly=True,
    )
    periodo_academico = fields.Char(
        string='Período Académico',
        related='subject_id.periodo_academico',
        store=True,
        readonly=True,
    )
    teacher_id = fields.Many2one(
        'gestion.teacher',
        string='Profesor',
        related='section_id.teacher_id',
        store=True,
        readonly=True,
    )
    student_nombre = fields.Char(
        string='Nombre',
        compute='_compute_student_name',
        store=True,
        readonly=True,
    )
    student_apellido = fields.Char(
        string='Apellido',
        compute='_compute_student_name',
        store=True,
        readonly=True,
    )
    detalle_ids = fields.One2many(
        'gestion.nota.final.detalle',
        'nota_final_id',
        string='Detalle de nota final',
    )
    nota_final = fields.Float(
        string='Nota Final',
        compute='_compute_nota_final',
        store=True,
    )
    promedio = fields.Float(
        string='Promedio',
        compute='_compute_promedio',
        store=True,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )

    # Separa el nombre completo en nombre y apellido
    @api.depends('student_id.name')
    def _compute_student_name(self):
        for rec in self:
            rec.student_nombre = ''
            rec.student_apellido = ''
            if rec.student_id and rec.student_id.name:
                parts = rec.student_id.name.strip().split()
                rec.student_nombre = parts[0] if parts else ''
                rec.student_apellido = ' '.join(parts[1:]) if len(parts) > 1 else ''

    # Despues de crear una nota final, genera las lineas de detalle (tipos de evaluacion)
    @api.model_create_multi
    def create(self, vals_list):
        records = super(NotaFinal, self).create(vals_list)
        for rec in records:
            rec._populate_detalle()
        return records

    def write(self, vals):
        result = super(NotaFinal, self).write(vals)
        if 'section_id' in vals or 'student_id' in vals:
            for rec in self:
                rec._populate_detalle()
        return result

    @api.onchange('section_id', 'student_id')
    def _onchange_section_or_student(self):
        for rec in self:
            rec._populate_detalle()

    # Crea una linea de detalle por cada tipo de evaluacion de la seccion
    def _populate_detalle(self):
        Tipo = self.env['gestion.tipo.evaluacion']
        Detalle = self.env['gestion.nota.final.detalle']
        for rec in self:
            if not rec.section_id or not rec.student_id:
                continue
            tipos = Tipo.search([('seccion_id', '=', rec.section_id.id)])
            existing_ids = rec.detalle_ids.mapped('tipo_evaluacion.id')
            for tipo in tipos:
                if tipo.id not in existing_ids:
                    Detalle.create({
                        'nota_final_id': rec.id,
                        'tipo_evaluacion': tipo.id,
                    })

    # Suma todos los aportes ponderados para obtener la nota final
    @api.depends('detalle_ids.aporte')
    def _compute_nota_final(self):
        for rec in self:
            rec.nota_final = sum(line.aporte for line in rec.detalle_ids)

    # Calcula el promedio general como promedio ponderado por los pesos de cada tipo
    @api.depends('detalle_ids.promedio_tipo', 'detalle_ids.peso')
    def _compute_promedio(self):
        for rec in self:
            lines = rec.detalle_ids
            if not lines:
                rec.promedio = 0.0
                continue
            # Suma de (promedio_tipo * peso) para cada tipo
            suma_ponderada = sum(line.promedio_tipo * (line.peso or 0.0) for line in lines)
            suma_pesos = sum(line.peso or 0.0 for line in lines)
            rec.promedio = suma_ponderada / suma_pesos if suma_pesos else 0.0


class GestionSeccionNotas(models.Model):
    _inherit = 'gestion.seccion'

    nota_final_ids = fields.One2many('gestion.nota.final', 'section_id', string='Notas Finales')
    subject_periodo_academico = fields.Char(
        string='Período Académico',
        related='subject_id.periodo_academico',
        store=True,
        readonly=True,
    )
    nota_final_count = fields.Integer(
        string='Notas Finales',
        compute='_compute_nota_final_count',
        store=True,
    )

    # Genera notas finales para todos los estudiantes que no tengan una en esta seccion
    # Nota: sin un campo student_ids en gestion.seccion, se generan para todos los estudiantes
    def _generar_notas_finales(self):
        self.ensure_one()
        NotaFinal = self.env['gestion.nota.final']
        estudiantes = self.env['gestion.student'].search([])
        for estudiante in estudiantes:
            # Verifica que no exista ya la combinacion estudiante + seccion
            existe = NotaFinal.search([
                ('student_id', '=', estudiante.id),
                ('section_id', '=', self.id),
            ], limit=1)
            if not existe:
                try:
                    NotaFinal.create({
                        'student_id': estudiante.id,
                        'section_id': self.id,
                    })
                except ValidationError:
                    continue

    # Al crear una seccion, genera las notas finales automaticamente
    @api.model_create_multi
    def create(self, vals_list):
        records = super(GestionSeccionNotas, self).create(vals_list)
        for rec in records:
            rec._generar_notas_finales()
        return records

    def write(self, vals):
        result = super(GestionSeccionNotas, self).write(vals)
        for rec in self:
            rec._generar_notas_finales()
        return result

    # Accion del boton "Ver estudiantes"
    def action_open_nota_final(self):
        self._generar_notas_finales()
        action = self.env.ref('gestion_nota_final.action_nota_final').read()[0]
        action['domain'] = [('section_id', 'in', self.ids)]
        action['context'] = {'default_section_id': self.id}
        return action

    @api.depends('nota_final_ids')
    def _compute_nota_final_count(self):
        for rec in self:
            rec.nota_final_count = len(rec.nota_final_ids)
