from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GestionMateria(models.Model):
    _name = "gestion.materia"
    _description = "Gestión de Materias Académicas"

    name = fields.Char(string="Nombre de la materia", required=True)
    codigo_materia = fields.Char(string="Código de la materia", required=True)

    periodo_academico = fields.Char(
        string="Período Académico", 
        required=True,
        default="2026-I", # Ideal para el año en curso
        help="Ejemplo: 2026-I o 2026-2027"
    )
    
    date_start = fields.Date(string="Fecha de Inicio", required=True)
    date_end = fields.Date(string="Fecha de Cierre", required=True)

    # Este campo se calcula solo, no se guarda en base de datos para que siempre esté actualizado al día de hoy
    estado_periodo = fields.Selection([
        ('abierto', 'En Curso'),
        ('cerrado', 'Finalizado')
    ], string="Estado del Período", compute="_compute_estado_periodo")

    @api.depends('date_start', 'date_end')
    def _compute_estado_periodo(self):
        hoy = fields.Date.today()
        for record in self:
            if record.date_start and record.date_end:
                # Si hoy está entre la fecha de inicio y la de cierre, está abierto
                if record.date_start <= hoy <= record.date_end:
                    record.estado_periodo = 'abierto'
                else:
                    record.estado_periodo = 'cerrado'
            else:
                record.estado_periodo = 'cerrado'

    teacher_id = fields.Many2one(
        comodel_name="gestion.teacher",
        string="Profesor titular",
        domain=[("is_teacher", "=", True)]
    )

    type = fields.Selection(
        selection=[
            ("obligatoria", "Obligatoria"),
            ("electiva", "Electiva"),
        ],
        string="Tipo de materia",
        default="electiva",
    )

    active = fields.Boolean(string="Activo", default=True)
    
    @api.constrains('name', 'codigo_materia')
    def checknotemptyfields(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("El nombre de la materia no puede estar vacío.")
            if not record.codigo_materia or not record.codigo_materia.strip():
                raise ValidationError("El código de la materia no puede estar vacío.")
