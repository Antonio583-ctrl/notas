from odoo import models, fields

class GestionSubmissionInherit(models.Model):
    # Heredamos el modelo del módulo de profesorado
    _inherit = 'gestion.submission'

    student_id = fields.Many2one('gestion.student', string='Estudiante', required=True, ondelete='cascade')


    def write(self, vals):
        # 1. Guardamos la nota normalmente en la entrega
        res = super(GestionSubmissionInherit, self).write(vals)
        
        # 2. Si el profesor modificó la calificación o las observaciones...
        if 'score' in vals or 'notes' in vals:
            for record in self:
               
                # ¡CORRECCIÓN AQUÍ! Ya no buscamos al estudiante, porque record.student_id YA es el estudiante
                estudiante_perfil = record.student_id

                if estudiante_perfil:
                    grade_env = self.env['grade.grade'].sudo()
                    
                    # Buscamos si ya existe una nota para no romper tu _check_unique_grade
                    nota_oficial = grade_env.search([
                        ('student_id', '=', estudiante_perfil.id),
                        ('activity_id', '=', record.activity_id.id)
                    ], limit=1)
                    
                    valores_nota = {
                        'student_id': estudiante_perfil.id,
                        'teacher_id': record.activity_id.teacher_id.id,
                        'activity_id': record.activity_id.id,
                        'score': record.score,
                        # Usamos record.notes (asegúrate de que el campo en submission se llame 'notes')
                        'teacher_feedback': record.notes, 
                        'description': f"Nota sincronizada desde la entrega web para {estudiante_perfil.name}",
                    }
                    
                    if nota_oficial:
                        # Si ya existe, actualizamos
                        nota_oficial.write(valores_nota)
                    else:
                        # Si no existe, creamos la nota oficial
                        grade_env.create(valores_nota)
                        
        return res