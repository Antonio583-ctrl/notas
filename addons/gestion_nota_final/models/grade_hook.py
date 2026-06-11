from odoo import api, models


class GradeHook(models.Model):
    """
    Hook que hereda el modelo grade.grade para disparar el recálculo
    de notas finales cuando se crea o modifica una calificación.
    
    Esto permite que el módulo gestion_nota_final reaccione a cambios
    en calificaciones sin modificar el módulo gestion_calificaciones.
    """
    _inherit = 'grade.grade'

    def write(self, vals):
        """
        Sobreescribe write para detectar cambios en nota o actividad.
        Cuando se modifica una calificación, busca las notas finales
        del estudiante en esa sección y las recalcula.
        """
        res = super().write(vals)
        if 'score' in vals or 'activity_id' in vals:
            self._disparar_recalculo_notas()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobreescribe create para disparar el recálculo al crear
        una nueva calificación.
        """
        records = super().create(vals_list)
        for rec in records:
            if rec.activity_id and rec.activity_id.section_id:
                notas = self.env['gestion.nota.final'].search([
                    ('student_id', '=', rec.student_id.id),
                    ('section_id', '=', rec.activity_id.section_id.id),
                ])
                if notas:
                    notas.action_recalculate()
        return records

    def _disparar_recalculo_notas(self):
        """
        Busca las notas finales del estudiante en la sección de la actividad
        y ejecuta el recálculo. Se llama desde create y write.
        """
        for rec in self:
            if rec.activity_id and rec.activity_id.section_id:
                notas = self.env['gestion.nota.final'].search([
                    ('student_id', '=', rec.student_id.id),
                    ('section_id', '=', rec.activity_id.section_id.id),
                ])
                if notas:
                    notas.action_recalculate()
