from odoo import models, fields

class GestionParticipacionLinea(models.Model):
    _name = 'gestion.participacion.linea'
    _description = 'Detalle de Participacion'

    participacion_id = fields.Many2one(
        'gestion.participacion.clase', 
        string='Sesion', 
        ondelete='cascade'
    )
    student_id = fields.Many2one(
        'gestion.student', 
        string='Estudiante', 
        required=True
    )
    participo = fields.Boolean(
        string='Participo',
        default=False
    )
    