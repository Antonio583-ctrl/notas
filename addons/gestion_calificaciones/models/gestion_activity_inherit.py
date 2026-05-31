# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import ValidationError

class Activity(models.Model):
    _inherit = 'gestion.activity'
    
    @api.constrains('name')
    def checkname(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("El nombre de la actividad no puede estar vacío.")