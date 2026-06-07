from odoo import api, fields, models


class NotaFinalLine(models.Model):
    _name = 'gestion.nota.final.line'
    _description = 'Detalle de nota final por tipo de evaluación'
    _order = 'tipo_evaluacion_id asc'

    nota_final_id = fields.Many2one(
        'gestion.nota.final',
        string='Nota Final',
        required=True,
        ondelete='cascade',
    )
    tipo_evaluacion_id = fields.Many2one(
        'gestion.tipo.evaluacion',
        string='Tipo de Evaluación',
        required=True,
        ondelete='cascade',
    )
    promedio_tipo = fields.Float(
        string='Promedio Tipo',
        compute='_compute_scores',
        store=True,
    )
    peso = fields.Float(
        string='Peso',
        related='tipo_evaluacion_id.porcentaje',
        store=True,
        readonly=True,
    )
    aporte = fields.Float(
        string='Aporte',
        compute='_compute_scores',
        store=True,
    )

    @api.depends('tipo_evaluacion_id', 'nota_final_id.student_id', 'nota_final_id.section_id')
    def _compute_scores(self):
        """Calcula el promedio y aporte según el tipo de evaluación.

        - Para tipos normales: toma las `grade.grade` relacionadas a la actividad y calcula promedio.
        - Para 'asistencia': calcula porcentaje de asistencias confirmadas (present) sobre el total
          de sesiones registradas y lo escala a 0-10.
        - Para 'participacion': agrega las entradas de participacion y promedia sus puntajes.
        """
        Grade = self.env['grade.grade']
        Attendance = self.env['gestion.attendance']
        AttendanceLine = self.env['gestion.attendance_line']
        Participacion = self.env['gestion.participacion']
        ParticipacionLine = self.env['gestion.participacion_line']

        for rec in self:
            rec.promedio_tipo = 0.0
            rec.aporte = 0.0
            if not rec.tipo_evaluacion_id or not rec.nota_final_id:
                continue
            student = rec.nota_final_id.student_id
            section = rec.nota_final_id.section_id
            if not student or not section:
                continue

            tipo_name = (rec.tipo_evaluacion_id.name or '').lower()

            # ASISTENCIA: calcular porcentaje de sesiones en las que estuvo presente
            if 'asistencia' in tipo_name:
                sessions = Attendance.search([
                    ('section_id', '=', section.id),
                    ('tipo_evaluacion_id', '=', rec.tipo_evaluacion_id.id),
                    ('state', '=', 'confirmed'),
                ])
                if sessions:
                    lines = AttendanceLine.search([
                        ('attendance_id', 'in', sessions.ids),
                        ('student_id', '=', student.id),
                    ])
                    if lines:
                        present = sum(1 for line in lines if getattr(line, 'present', False))
                        # escala a 0-10
                        promedio = (present / len(lines)) * 10.0
                        rec.promedio_tipo = promedio
                        rec.aporte = promedio * (rec.peso or 0.0)
                        continue

            # PARTICIPACIÓN: promediar puntajes de participaciones si existen
            if 'participacion' in tipo_name or 'participación' in tipo_name:
                parts = Participacion.search([
                    ('section_id', '=', section.id),
                    ('tipo_evaluacion_id', '=', rec.tipo_evaluacion_id.id),
                ])
                if parts:
                    plines = ParticipacionLine.search([
                        ('participacion_id', 'in', parts.ids),
                        ('student_id', '=', student.id),
                    ])
                    scores = plines.mapped('score') if plines else []
                    if scores:
                        promedio = sum(scores) / len(scores)
                        rec.promedio_tipo = promedio
                        rec.aporte = promedio * (rec.peso or 0.0)
                        continue

            # CASO GENERAL: notas asociadas a actividades (grade.grade)
            grades = Grade.search([
                ('student_id', '=', student.id),
                ('activity_id.section_id', '=', section.id),
                ('activity_id.tipo_evaluacion_id', '=', rec.tipo_evaluacion_id.id),
            ])
            if not grades:
                continue
            scores = grades.mapped('score')
            if not scores:
                continue
            rec.promedio_tipo = sum(scores) / len(scores)
            rec.aporte = rec.promedio_tipo * (rec.peso or 0.0)
