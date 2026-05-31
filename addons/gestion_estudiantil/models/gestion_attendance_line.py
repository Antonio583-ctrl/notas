from odoo import models, fields

class GestionAttendanceLine(models.Model):
    _name = 'gestion.attendance_line'
    _description = 'Línea de Asistencia'

    attendance_id = fields.Many2one('gestion.attendance', string="Registro de Asistencia", ondelete='cascade')
    student_id = fields.Many2one('gestion.student', string="Estudiante", required=True) 
    present = fields.Boolean(string="Presente", default=True)
