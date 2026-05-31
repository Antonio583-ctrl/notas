from odoo import models, fields


class GestionActivityInherit(models.Model):
    _inherit = 'gestion.activity'

    subject_id = fields.Many2one('gestion.materia', string='Materia', required=True)
    
    # El domain hace que solo salgan las secciones de la materia seleccionada
    section_id = fields.Many2one(
        'gestion.seccion', 
        string='Sección', 
        domain="[('subject_id', '=', subject_id)]",
        required=True
    )
    
    periodo_academico = fields.Char(string='Periodo Académico', default='2024-2025', required=True)