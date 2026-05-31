# -*- coding: utf-8 -*-
from odoo import models, fields, api

class GestionAttendance(models.Model):
    _name = 'gestion.attendance'
    _description = 'Registro de Asistencia'

    date = fields.Date(string="Fecha", default=fields.Date.today, required=True)
    
    subject_id = fields.Many2one(
        'gestion.materia', 
        string="Materia", 
        required=True
    )

    section_id = fields.Many2one(
        'gestion.seccion', 
        string="Sección", 
        required=True
    ) 
    
    teacher_id = fields.Many2one(
        related='section_id.teacher_id', 
        string="Profesor Responsable", 
        readonly=True, 
        store=True
    )

    estado_periodo_materia = fields.Selection(
        related='subject_id.estado_periodo',
        string="Estado de la Materia",
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado')
    ], string="Estado", default='draft')
    
    # Este es el campo que falta y causa el error
    confirmed = fields.Boolean(string="Confirmado", compute="_compute_confirmed", store=True)

    attendance_line_ids = fields.One2many(
        'gestion.attendance_line', 
        'attendance_id', 
        string="Lista de Estudiantes"
    )

    @api.depends('state')
    def _compute_confirmed(self):
        for record in self:
            record.confirmed = (record.state == 'confirmed')

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    @api.onchange('subject_id')
    def _onchange_subject_id(self):
        """Si el profesor cambia la materia, limpiamos la sección y la lista de estudiantes para evitar errores."""
        self.section_id = False
        self.attendance_line_ids = [(5, 0, 0)]    

    @api.onchange('section_id')
    def _onchange_section_id(self):
        """Carga automáticamente los estudiantes de la sección seleccionada."""
        if self.section_id and self.section_id.student_ids:
            # Limpiar líneas existentes para evitar duplicados si se cambia de sección
            self.attendance_line_ids = [(5, 0, 0)]
            
            lines = []
            for student_partner in self.section_id.student_ids:
                lines.append((0, 0, {
                    'student_id': student_partner.id,
                    'present': False
                }))
            self.attendance_line_ids = lines    
    
       



    