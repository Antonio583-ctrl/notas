# -*- coding: utf-8 -*-
from odoo import models, fields

class GestionParticipacionLine(models.Model):
    _name = 'gestion.participacion.line'
    _description = 'Línea de Participación por Estudiante'

    participacion_id = fields.Many2one(
        'gestion.participacion.clase',
        string='Sesión de Participación',
        required=True,
        ondelete='cascade'
    )
    
    student_id = fields.Many2one(
        'gestion.student',
        string='Estudiante',
        required=True
    )
    
    participo = fields.Boolean(
        string='Participó',
        default=False,
        help='Marcar si el estudiante participó en esta sesión'
    )