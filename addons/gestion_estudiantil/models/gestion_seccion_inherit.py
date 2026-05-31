from odoo import models, fields

class GestionSeccionInherit(models.Model):
    _inherit = "gestion.seccion"
    student_ids = fields.Many2many("gestion.student", string="Estudiantes")