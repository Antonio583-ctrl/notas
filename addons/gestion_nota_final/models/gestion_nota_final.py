from odoo import models, fields, api

class NotaFinal(models.Model):
    _name = 'nota.final'
    _description = 'Nota Final'
    _rec_name = 'student_id'
    _sql_constraints = [
        ('student_section_unique', 'unique(student_id, section_id)', 'Ya existe una nota final para este estudiante en esta sección.'),
    ]

    student_id = fields.Many2one(
        'gestion.student',
        string='Estudiante',
        ondelete="cascade",
        required=True,        
    )
    
    section_id = fields.Many2one(
        "gestion.seccion",
        string="Sección",
        ondelete="cascade",
        required=True
    )
    
    subject_id = fields.Many2one(
        "gestion.materia",
        string="Materia",
        related="section_id.subject_id",  # viene de section_id → subject_id
        store=True,  # se guarda en BD (evita joins repetidos)
        readonly=True
    )
    
    periodo_academico = fields.Char(
        string="Período Académico",
        related="subject_id.periodo_academico",
        store=True,
        readonly=True
    )
    
    teacher_id = fields.Many2one(
        "gestion.teacher",
        string="Profesor",
        related="section_id.teacher_id",
        store=True,
        readonly=True
    )
    
    active = fields.Boolean(
        string="Activo", 
        default=True
    )
    
    detalle_ids = fields.One2many(
        "nota.final.detalle",
        "nota_final_id",
        string="detalle_ids"
    )
    
    nota_final = fields.Float(
        string="Nota Final",
        compute="_compute_nota_final",
        store=True
    )
    
    promedio = fields.Float(
        string="Promedio",
        compute="_compute_promedio",
        store=True
    )

    # Cuando se crea un nota.final, genera sus líneas de detalle.
    @api.model_create_multi
    def create(self, vals_list):
        records = super(NotaFinal, self).create(vals_list)
        for rec in records:
            rec._populate_detalle()
        return records

    # cuando se actualiza el estudiante o la sección, vuelve a revisar/crear líneas.
    def write(self, vals):
        result = super(NotaFinal, self).write(vals)
        if 'section_id' in vals or 'student_id' in vals:
            for rec in self:
                rec._populate_detalle()
        return result

    # cuando el usuario cambia esos campos en el formulario, llama a _populate_detalle para actualizar las líneas en tiempo real.
    @api.onchange('section_id', 'student_id')
    def _onchange_section_or_student(self):
        for rec in self:
            rec._populate_detalle()

    # crea una línea por cada tipo de evaluación de la sección.
    def _populate_detalle(self):
        Tipo = self.env['gestion.tipo.evaluacion']
        Detalle = self.env['nota.final.detalle']
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

    # suma los aportes de todas las líneas.
    @api.depends('detalle_ids.aporte')
    def _compute_nota_final(self):
        for rec in self:
            rec.nota_final = sum(line.aporte for line in rec.detalle_ids)

    # promedia los promedios por tipo de evaluación.
    @api.depends('detalle_ids.promedio_tipo')
    def _compute_promedio(self):
        for rec in self:
            lines = rec.detalle_ids
            rec.promedio = sum(line.promedio_tipo for line in lines) / len(lines) if lines else 0.0