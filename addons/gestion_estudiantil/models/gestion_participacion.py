# -*- coding: utf-8 -*-
from odoo import models, fields, api

class GestionParticipacionClase(models.Model):
    _name = 'gestion.participacion.clase'
    _description = 'Sesión de Participación en Clase'
    _rec_name = 'fecha'
    _order = 'fecha desc, seccion_id'

    fecha = fields.Date(
        string='Fecha de la Sesión',
        required=True,
        default=fields.Date.today
    )
    
    subject_id = fields.Many2one(
        'gestion.materia',
        string='Materia',
        required=True
    )
    
    seccion_id = fields.Many2one(
        'gestion.seccion',
        string='Sección',
        required=True,
        domain="[('subject_id', '=', subject_id), ('teacher_id.user_id', '=', uid)]"
    )
    
    teacher_id = fields.Many2one(
        'gestion.teacher',
        string='Profesor',
        related='seccion_id.teacher_id',
        store=True,
        readonly=True
    )
    
    participacion_line_ids = fields.One2many(
        'gestion.participacion.line',
        'participacion_id',
        string='Estudiantes'
    )
    
    @api.onchange('subject_id')
    def _onchange_subject_id(self):
        self.seccion_id = False
        self.participacion_line_ids = [(5, 0, 0)]
    
    @api.onchange('seccion_id')
    def _onchange_seccion_id(self):
        if self.seccion_id and self.seccion_id.student_ids:
            self.participacion_line_ids = [(5, 0, 0)]
            lines = []
            for student in self.seccion_id.student_ids:
                lines.append((0, 0, {
                    'student_id': student.id,
                    'participo': False
                }))
            self.participacion_line_ids = lines