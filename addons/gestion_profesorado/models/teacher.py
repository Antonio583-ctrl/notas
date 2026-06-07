from odoo import models, fields, api

#EXTENSIÓN DE RES.PARTNER
# Necesaria para que el módulo de Secciones pueda filtrar profesores

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_teacher = fields.Boolean(
        string="Es Profesor", 
        default=False,
        help="Flag técnico para que el módulo de secciones reconozca a este contacto como profesor."
    )

class Teacher(models.Model):
    _name = 'gestion.teacher'
    _description = 'Teacher'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Related User')

    # Cambiamos el string a uno genérico para que no diga "Docente" por defecto
    signature = fields.Binary(
        string="Firma Digital",
        help="Firma digital para la generación de actas oficiales y reportes."
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(Teacher, self).create(vals_list)
        for record in records:
            record.partner_id.is_teacher = True # Force is_teacher flag
            if not record.user_id and record.email:
                # Create user automatically
                user_vals = {
                    'name': record.name,
                    'login': record.email,
                    'partner_id': record.partner_id.id,
                    'groups_id': [(4, self.env.ref('gestion_profesorado.group_profesor').id)],
                    'action_id': self.env.ref('gestion_estudiantil.action_estudiantes_final').id,
                }
                user = self.env['res.users'].create(user_vals)
                record.user_id = user
        return records

    # Estos campos se dejan comentados para evitar errores de relación 
    # hasta que los modelos de Materias y Secciones existan en el sistema.
    
    # subject_ids = fields.One2many(
    #     'gestion.subject', 
    #     'teacher_id', 
    #     string="Materias",
    #     help="Materias de las cuales es el titular responsable."
    # )

    # section_ids = fields.One2many(
    #     'gestion.section', 
    #     'teacher_id', 
    #     string="Secciones",
    #     help="Secciones específicas que tiene asignadas actualmente."
    # )

    # Nota: 'user_id' y 'name' ya vienen heredados de res.users