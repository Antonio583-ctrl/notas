from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GestionActivity(models.Model):
    _name = 'gestion.activity'
    _description = 'Actividad Académica'

    name = fields.Char(string='Título de la Tarea', required=True)
    description = fields.Html(string='Instrucciones')
    date_deadline = fields.Date(string='Fecha de Entrega')
    
    teacher_id = fields.Many2one('gestion.teacher', string='Profesor Responsable', required=True)
    
    
    submission_ids = fields.One2many('gestion.submission', 'activity_id', string='Entregas')

    @api.constrains('name')
    def checknotemptyfields(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("El título de la actividad no puede estar vacío.")

