from odoo import models, fields, api

class GestionSubmission(models.Model):
    _name = 'gestion.submission'
    _description = 'Entrega de Alumno'

    activity_id = fields.Many2one('gestion.activity', string='Tarea', required=True, ondelete='cascade')
        
    
    file_data = fields.Binary(string='Archivo de Tarea')
    file_name = fields.Char(string='Nombre del Archivo')
    
    submission_date = fields.Date(string='Fecha de Envío', default=fields.Date.today)
    score = fields.Float(string='Calificación')
    notes = fields.Text(string='Observaciones del Profesor')