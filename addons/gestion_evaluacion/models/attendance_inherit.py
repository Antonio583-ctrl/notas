# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class GestionAttendance(models.Model):
    _inherit = 'gestion.attendance'

    tipo_evaluacion_id = fields.Many2one(
        'gestion.tipo.evaluacion', 
        string='Tipo de Evaluación'
    )

    @api.onchange('section_id')
    def _onchange_section_id_auto_assign_evaluacion(self):
        if self.section_id:
            # Lógica Automática:
            # Se busca el tipo de evaluación llamado "Asistencia" de la sección seleccionada.
            # Supuesto documentado: Se realiza una búsqueda por coincidencia exacta (no sensible a mayúsculas/minúsculas)
            # y se limita a 1 resultado para evitar ambigüedades en caso de haber duplicados en la base de datos.
            tipo_eval = self.env['gestion.tipo.evaluacion'].search([
                ('seccion_id', '=', self.section_id.id),
                ('name', '=ilike', 'Asistencia')
            ], limit=1)
            
            if tipo_eval:
                self.tipo_evaluacion_id = tipo_eval.id
            else:
                self.tipo_evaluacion_id = False
