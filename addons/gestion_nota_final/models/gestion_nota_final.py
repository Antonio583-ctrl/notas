from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


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
    teacher_id = fields.Many2one(
        'gestion.teacher',
        string='Profesor',
        related='section_id.teacher_id',
        store=True,
        readonly=True,
    )
    student_nombre = fields.Char(
        string='Nombre',
        related='student_id.partner_id.name',
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
    recalc_trigger = fields.Integer(
        string='Recalcular Trigger',
        default=0,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """Asegura que los registros de nota final existan para todos los estudiantes antes de buscar."""
        if not self.env.context.get('bypass_ensure'):
            self.sudo().with_context(bypass_ensure=True)._ensure_nota_final_records()
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def _ensure_nota_final_records(self):
        """Asegura que todos los estudiantes inscritos en secciones activas tengan su registro de nota final."""
        Seccion = self.env['gestion.seccion']
        NotaFinal = self.env['gestion.nota.final'].sudo().with_context(bypass_ensure=True)
        
        # Buscar todas las secciones activas (abiertas o en progreso)
        secciones = Seccion.search([('state', 'in', ['abierto', 'en progreso'])])
        if not secciones:
            return
            
        # Buscar todas las notas finales ya existentes para estas secciones
        existentes = NotaFinal.search([('section_id', 'in', secciones.ids)])
        existentes_map = {(r.student_id.id, r.section_id.id) for r in existentes}
        
        notas_to_create = []
        for seccion in secciones:
            for student in seccion.student_ids:
                if (student.id, seccion.id) not in existentes_map:
                    notas_to_create.append({
                        'student_id': student.id,
                        'section_id': seccion.id,
                    })
                    
        if notas_to_create:
            created_notas = NotaFinal.create(notas_to_create)
            # Recalcular las notas recién creadas
            created_notas.action_recalculate()

    @api.model
    def trigger_recalculate(self, student_id, section_id):
        """Busca o crea la nota final para un estudiante y sección, y fuerza su recálculo."""
        if not student_id or not section_id:
            return
        NotaFinal = self.env['gestion.nota.final'].sudo().with_context(bypass_ensure=True)
        nota = NotaFinal.search([
            ('student_id', '=', student_id),
            ('section_id', '=', section_id),
        ], limit=1)
        if not nota:
            nota = NotaFinal.create({
                'student_id': student_id,
                'section_id': section_id,
            })
        nota.action_recalculate()

    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Al leer la lista, recalculamos notas automáticamente."""
        _logger.info(f"[NOTA_FINAL] search_read disparado")
        records = self.search(domain or [], offset=offset, limit=limit, order=order)
        _logger.info(f"[NOTA_FINAL] Registros encontrados: {len(records)}")
        records.sudo().action_recalculate()
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    def action_recalculate(self):
        """Recalcula todas las notas finales e incrementa recalc_trigger."""
        for rec in self:
            rec._populate_detalle()
            # Al modificar recalc_trigger, Odoo recomputa y actualiza los campos almacenados
            rec.write({'recalc_trigger': rec.recalc_trigger + 1})
        return True

    # Cada vez que se cree una NotaFinal, se asegura su desglose
    def create(self, vals_list):
        records = super().create(vals_list)
        records.sudo()._populate_detalle()
        return records

    # ==================== MÉTODOS DE APOYO ====================
    def _populate_detalle(self):
        """Crea las líneas de detalle que falten y elimina las que ya no correspondan."""
        Tipo = self.env['gestion.tipo.evaluacion']
        Detalle = self.env['gestion.nota.final.detalle']
        for rec in self:
            if not rec.section_id or not rec.student_id:
                continue
            tipos = Tipo.search([('seccion_id', '=', rec.section_id.id)])
            rec.detalle_ids.filtered(lambda d: d.tipo_evaluacion.id not in tipos.ids).unlink()
            existing_ids = rec.detalle_ids.mapped('tipo_evaluacion.id')
            for tipo in tipos:
                if tipo.id not in existing_ids:
                    Detalle.create({
                        'nota_final_id': rec.id,
                        'tipo_evaluacion': tipo.id,
                    })

    # ==================== CAMPOS COMPUTADOS ====================
    @api.depends('recalc_trigger', 'detalle_ids.aporte')
    def _compute_nota_final(self):
        """Suma los aportes ponderados de cada tipo para obtener la nota final."""
        for rec in self:
            rec.nota_final = sum(d.aporte for d in rec.detalle_ids)

    @api.depends('recalc_trigger', 'detalle_ids.promedio_tipo', 'detalle_ids.peso')
    def _compute_promedio(self):
        """Calcula el promedio general ponderado por los pesos de cada tipo."""
        for rec in self:
            lines = rec.detalle_ids
            if not lines:
                rec.promedio = 0.0
                continue
            weighted = sum(l.promedio_tipo * (l.peso or 0.0) for l in lines)
            total_weight = sum(l.peso or 0.0 for l in lines)
            rec.promedio = weighted / total_weight if total_weight else 0.0
