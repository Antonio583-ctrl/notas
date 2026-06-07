from odoo import api, fields, models


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

    @api.depends('tipo_evaluacion', 'nota_final_id.student_id', 'nota_final_id.section_id')
    def _compute_promedio(self):
        Grade = self.env['grade.grade']
        Attendance = self.env['gestion.attendance']
        AttendanceLine = self.env['gestion.attendance_line']

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

            # 1) Si el tipo es ASISTENCIA, usar las sesiones de asistencia confirmadas
            if 'asistencia' in tipo_name:
                sessions = Attendance.search([
                    ('section_id', '=', section.id),
                    ('tipo_evaluacion_id', '=', rec.tipo_evaluacion.id),
                    ('state', '=', 'confirmed'),
                ])
                if sessions:
                    lines = AttendanceLine.search([
                        ('attendance_id', 'in', sessions.ids),
                        ('student_id', '=', student.id),
                    ])
                    if lines:
                        present = sum(1 for line in lines if line.present)
                        promedio = (present / len(lines)) * 10.0
                        rec.promedio_tipo = promedio
                        rec.aporte = promedio * (rec.peso or 0.0)
                        continue

            # 2) Si el tipo es PARTICIPACION, usar las entradas de participacion (si existe el modelo)
            if 'participacion' in tipo_name or 'participación' in tipo_name:
                if 'gestion.participacion' in self.env.registry.models:
                    Participacion = self.env['gestion.participacion']
                    ParticipacionLine = self.env['gestion.participacion_line']
                    parts = Participacion.search([
                        ('section_id', '=', section.id),
                        ('tipo_evaluacion_id', '=', rec.tipo_evaluacion.id),
                    ])
                    if parts:
                        plines = ParticipacionLine.search([
                            ('participacion_id', 'in', parts.ids),
                            ('student_id', '=', student.id),
                        ])
                        if plines:
                            scores = plines.mapped('score')
                            if scores:
                                promedio = sum(scores) / len(scores)
                                rec.promedio_tipo = promedio
                                rec.aporte = promedio * (rec.peso or 0.0)
                                continue

            # 3) CASO GENERAL: buscar calificaciones en grade.grade vinculadas a actividades
            grades = Grade.search([
                ('student_id', '=', student.id),
                ('activity_id.section_id', '=', section.id),
                ('activity_id.tipo_evaluacion_id', '=', rec.tipo_evaluacion.id),
            ])
            if not grades:
                continue
            scores = grades.mapped('score')
            if not scores:
                continue
            promedio = sum(scores) / len(scores)
            rec.promedio_tipo = promedio
            rec.aporte = promedio * (rec.peso or 0.0)
