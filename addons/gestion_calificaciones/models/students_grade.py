from odoo import models, fields
from odoo.exceptions import ValidationError

class StudentGrade(models.Model):
    _name = 'gestion.student.grade'
    _description = 'Historial de Calificaciones'

    student_id = fields.Many2one(
        'gestion.student',
        string='Estudiante',
        required=True,
        ondelete='cascade'
    )

    activity_id = fields.Many2one(
        'gestion.activity',
        string='Actividad',
        required=True
    )
       
    score = fields.Float(string='Calificación', required=True)
    description = fields.Text(string='Descripción')
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now)
