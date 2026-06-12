from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class NotaFinalDetalle(models.Model):
    _name = 'gestion.nota.final.detalle'
    _description = 'Detalle de Nota Final'

    nota_final_id = fields.Many2one(
        'gestion.nota.final',
        string='Nota Final',
        ondelete="cascade",
        required=True,
    )

    tipo_evaluacion = fields.Many2one(
        'gestion.tipo.evaluacion',
        string='Tipo de Evaluación',
        ondelete="cascade",
        required=True,
    )

    peso = fields.Float(
        string='Peso',
        related='tipo_evaluacion.porcentaje',
        store=True,
        readonly=True,
    )

    promedio_tipo = fields.Float(
        string='Promedio Tipo',
        compute='_compute_promedio',
        store=True,
    )

    aporte = fields.Float(
        string='Aporte',
        compute='_compute_promedio',
        store=True,
    )

    @api.depends('tipo_evaluacion', 'nota_final_id.student_id', 'nota_final_id.section_id', 'tipo_evaluacion.porcentaje', 'nota_final_id.recalc_trigger')
    def _compute_promedio(self):
        """Cálculo principal: se ejecuta automáticamente al leer los campos.
        Maneja asistencia, participación y calificaciones generales."""
        for rec in self:
            rec.promedio_tipo = 0.0
            rec.aporte = 0.0
            if not rec.tipo_evaluacion or not rec.nota_final_id:
                continue
            student = rec.nota_final_id.student_id
            section = rec.nota_final_id.section_id
            if not student or not section:
                continue
            tipo_name = (rec.tipo_evaluacion.name or '').lower()

            # 1) ASISTENCIA: busca sesiones de asistencia confirmadas
            if 'asistencia' in tipo_name:
                rec._calcular_desde_asistencia(student, section)
                continue

            # 2) PARTICIPACIÓN: busca registros de participación confirmados
            if 'participacion' in tipo_name or 'participación' in tipo_name:
                rec._calcular_desde_participacion(student, section)
                continue

            # 3) CASO GENERAL: calificaciones normales de actividades
            rec._calcular_desde_calificaciones()

    # ==================== MÉTODOS PRIVADOS POR TIPO ====================
    def _calcular_desde_asistencia(self, student, section):
        Attendance = self.env['gestion.attendance']
        AttendanceLine = self.env['gestion.attendance_line']
        sessions = Attendance.search([
            ('section_id', '=', section.id),
            ('state', '=', 'confirmed'),
        ])
        if not sessions:
            return
        lines = AttendanceLine.search([
            ('attendance_id', 'in', sessions.ids),
            ('student_id', '=', student.id),
        ])
        if not lines:
            return
        present = sum(1 for line in lines if line.present)
        promedio = (present / len(lines)) * 10.0
        self.promedio_tipo = promedio
        self.aporte = promedio * (self.peso or 0.0)

    def _calcular_desde_participacion(self, student, section):
        if 'gestion.participacion.clase' not in self.env.registry.models:
            return
        Participacion = self.env['gestion.participacion.clase']
        ParticipacionLine = self.env['gestion.participacion.line']
        parts = Participacion.search([
            ('seccion_id', '=', section.id),
        ])
        if not parts:
            return
        plines = ParticipacionLine.search([
            ('participacion_id', 'in', parts.ids),
            ('student_id', '=', student.id),
        ])
        if not plines:
            return
        total_sesiones = len(plines)
        veces_participo = sum(1 for line in plines if line.participo)
        promedio = (veces_participo / total_sesiones) * 10.0 if total_sesiones else 0.0
        self.promedio_tipo = promedio
        self.aporte = promedio * (self.peso or 0.0)

    def _calcular_desde_calificaciones(self):
        Grade = self.env['grade.grade']
        grades = Grade.search([
            ('student_id', '=', self.nota_final_id.student_id.id),
            ('activity_id.section_id', '=', self.nota_final_id.section_id.id),
            ('activity_id.tipo_evaluacion_id', '=', self.tipo_evaluacion.id),
        ])
        _logger.info(f"[NOTA_FINAL] Buscando grades para tipo={self.tipo_evaluacion.name}, student={self.nota_final_id.student_id.name}, section={self.nota_final_id.section_id.name}, encontrados={len(grades)}")
        if not grades:
            return
        scores = grades.mapped('score')
        _logger.info(f"[NOTA_FINAL] Scores encontrados: {scores}")
        if not scores:
            return
        promedio = sum(scores) / len(scores)
        _logger.info(f"[NOTA_FINAL] Promedio calculado: {promedio}")
        self.promedio_tipo = promedio
        self.aporte = promedio * (self.peso or 0.0)
