# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GestionPeriodo(models.Model):
    _name = 'gestion.periodo'
    _description = 'Período Académico'

    name = fields.Char(string='Nombre del Período', required=True)
    activo = fields.Boolean(string='Activo', default=True)

    @api.constrains('activo')
    def _check_single_active_period(self):
        for record in self:
            if record.activo:
                other_active = self.search([
                    ('activo', '=', True),
                    ('id', '!=', record.id)
                ])
                if other_active:
                    raise ValidationError("Solo puede haber un período académico activo a la vez.")
