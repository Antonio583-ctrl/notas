from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GestionSeccion(models.Model):
    _name = "gestion.seccion"
    _description = "Secciones de Materias"

    name = fields.Char(required=True)
    subject_id = fields.Many2one("gestion.materia", string="Materia", required=True)
    teacher_id = fields.Many2one("gestion.teacher", string="Profesor", domain=[("is_teacher", "=", True)])
    state = fields.Selection(
        [
            ("abierto", "Abierto"),
            ("en progreso", "En Progreso"),
            ("finalizado", "Finalizado"),
        ],
        default="abierto",
    )

    @api.constrains('name')
    def checknotemptyfields(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("El nombre de la sección no puede estar vacío.")
