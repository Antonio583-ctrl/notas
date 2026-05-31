from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Grade(models.Model):
    _name = 'grade.grade'
    _description = 'Calificación'
    _rec_name = 'student_id'

    student_id = fields.Many2one(
        'gestion.student',
        string='Estudiante',
        required=True,
        help='Selecciona el estudiante.'
    )

    teacher_id = fields.Many2one('gestion.teacher', string='Docente')
    activity_id = fields.Many2one('gestion.activity', string='Actividad', required=True)

    score = fields.Float(string='Calificación', help='Calificación numérica obtenida.')
    teacher_feedback = fields.Text(string='Comentarios del Profesor', help='Comentarios del profesor sobre el desempeño.')
    
    date = fields.Date(string="Fecha", default=fields.Date.context_today)
    description = fields.Text(string='Descripción de la Nota')

    # Logic from develop (Unique Constraints)
    @api.constrains('student_id', 'activity_id')
    def _check_unique_grade(self):
        for record in self:
            existing = self.search([
                ('student_id', '=', record.student_id.id),
                ('activity_id', '=', record.activity_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(
                    f"El estudiante {record.student_id.name} ya tiene una calificación registrada para la actividad '{record.activity_id.name}'."
                )

    # Logic from develop (History Tracking)
    @api.model_create_multi
    def create(self, vals_list):
        records = super(Grade, self).create(vals_list)
        for record in records:
            self.env['gestion.student.grade'].sudo().create({
                'student_id': record.student_id.id,
                'activity_id': record.activity_id.id,
                'score': record.score,
                'description': f'Nota registrada para {record.student_id.name}'
            })
        return records

    def write(self, vals):
        res = super(Grade, self).write(vals)
        if 'score' in vals or 'activity_id' in vals:
            for record in self:
                self.env['gestion.student.grade'].sudo().create({
                    'student_id': record.student_id.id,
                    'activity_id': record.activity_id.id,
                    'score': record.score,
                    'description': f'Actualización de nota para {record.student_id.name}'
                })
        return res