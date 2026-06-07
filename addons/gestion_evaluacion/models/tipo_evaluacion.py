# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GestionTipoEvaluacion(models.Model):
    _name = 'gestion.tipo.evaluacion'
    _description = 'Tipo de Evaluación'

    name = fields.Char(string='Nombre', required=True)
    materia_id = fields.Many2one('gestion.materia', string='Materia', required=True)
    seccion_id = fields.Many2one(
        'gestion.seccion', 
        string='Sección', 
        required=True,
        domain="[('subject_id', '=', materia_id)]"
    )

    porcentaje = fields.Float(string='Porcentaje (Peso)', required=True, default=0.0)
    periodo_id = fields.Many2one('gestion.periodo', string='Período Académico', required=True)

    # Validacion de suma de porcentajes por sección no supera 1.0 (100%)
    @api.constrains('porcentaje', 'seccion_id')
    def _check_porcentaje_total(self):
        for record in self:
            tipos = self.search([
                ('seccion_id', '=', record.seccion_id.id),
                ('id', '!=', record.id)
            ])
            suma = record.porcentaje + sum(t.porcentaje for t in tipos)
            if round(suma, 4) > 1.0:
                raise ValidationError(
                    _("La suma de porcentajes para la sección '%s' supera el 100%% (1.0). Suma total: %.2f")
                    % (record.seccion_id.name, suma)
                )
            if record.porcentaje <= 0:
                raise ValidationError(_("El porcentaje debe ser estrictamente mayor a 0 (0%)."))

    # Asignar período activo por defecto
    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        periodo_activo = self.env['gestion.periodo'].search([('activo', '=', True)], limit=1)
        if periodo_activo:
            defaults['periodo_id'] = periodo_activo.id
        return defaults

    # Validacion de que el período este activo
    @api.constrains('periodo_id')
    def _check_periodo_activo(self):
        for record in self:
            if record.periodo_id and not record.periodo_id.activo:
                raise ValidationError(_("Solo se puede asignar un período académico activo."))