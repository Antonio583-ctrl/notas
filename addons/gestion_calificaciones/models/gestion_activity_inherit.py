# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Activity(models.Model):
    _inherit = 'gestion.activity'

    tipo_evaluacion_id = fields.Many2one('gestion.tipo.evaluacion', string='Tipo de Evaluación')

    @api.constrains('name')
    def checkname(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("El nombre de la actividad no puede estar vacío.")