from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class GradeHook(models.Model):
    """
    Hook que hereda el modelo grade.grade para disparar el recálculo
    de notas finales cuando se crea, modifica o elimina una calificación.
    """
    _inherit = 'grade.grade'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.student_id and rec.activity_id and rec.activity_id.section_id:
                self.env['gestion.nota.final'].trigger_recalculate(rec.student_id.id, rec.activity_id.section_id.id)
        return records

    def write(self, vals):
        # Almacenar datos antiguos antes de actualizar
        old_data = {}
        if 'score' in vals or 'activity_id' in vals or 'student_id' in vals:
            for rec in self:
                old_data[rec.id] = {
                    'student_id': rec.student_id.id,
                    'section_id': rec.activity_id.section_id.id if (rec.activity_id and rec.activity_id.section_id) else False
                }
        
        res = super().write(vals)
        
        if 'score' in vals or 'activity_id' in vals or 'student_id' in vals:
            for rec in self:
                # Recalcular nuevo estudiante/sección
                if rec.student_id and rec.activity_id and rec.activity_id.section_id:
                    self.env['gestion.nota.final'].trigger_recalculate(rec.student_id.id, rec.activity_id.section_id.id)
                # Recalcular antiguo si cambió
                old = old_data.get(rec.id)
                if old and old['student_id'] and old['section_id']:
                    new_student_id = rec.student_id.id
                    new_section_id = rec.activity_id.section_id.id if (rec.activity_id and rec.activity_id.section_id) else False
                    if old['student_id'] != new_student_id or old['section_id'] != new_section_id:
                        self.env['gestion.nota.final'].trigger_recalculate(old['student_id'], old['section_id'])
        return res

    def unlink(self):
        records_to_recalc = []
        for rec in self:
            if rec.student_id and rec.activity_id and rec.activity_id.section_id:
                records_to_recalc.append((rec.student_id.id, rec.activity_id.section_id.id))
        
        res = super().unlink()
        
        for student_id, section_id in records_to_recalc:
            self.env['gestion.nota.final'].trigger_recalculate(student_id, section_id)
        return res


class ActivityHook(models.Model):
    """
    Hook que hereda gestion.activity para recalcular notas finales
    si se cambia el tipo de evaluación o sección de una actividad.
    """
    _inherit = 'gestion.activity'

    def write(self, vals):
        old_sections = {}
        if 'tipo_evaluacion_id' in vals or 'section_id' in vals:
            for rec in self:
                old_sections[rec.id] = rec.section_id.id
        
        res = super().write(vals)
        
        if 'tipo_evaluacion_id' in vals or 'section_id' in vals:
            for rec in self:
                if rec.section_id:
                    for student in rec.section_id.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, rec.section_id.id)
                old_sect_id = old_sections.get(rec.id)
                if old_sect_id and old_sect_id != rec.section_id.id:
                    old_sect = self.env['gestion.seccion'].browse(old_sect_id)
                    for student in old_sect.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, old_sect_id)
        return res


class AttendanceHook(models.Model):
    """
    Hook que hereda gestion.attendance para recalcular notas finales
    cuando el estado de asistencia cambia (por ejemplo, a confirmado).
    """
    _inherit = 'gestion.attendance'

    def write(self, vals):
        old_sections = {}
        if 'state' in vals or 'section_id' in vals:
            for rec in self:
                old_sections[rec.id] = rec.section_id.id
        
        res = super().write(vals)
        
        if 'state' in vals or 'section_id' in vals:
            for rec in self:
                if rec.section_id:
                    for student in rec.section_id.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, rec.section_id.id)
                old_sect_id = old_sections.get(rec.id)
                if old_sect_id and old_sect_id != rec.section_id.id:
                    old_sect = self.env['gestion.seccion'].browse(old_sect_id)
                    for student in old_sect.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, old_sect_id)
        return res

    def unlink(self):
        records_to_recalc = []
        for rec in self:
            if rec.section_id:
                records_to_recalc.append(rec.section_id)
        
        res = super().unlink()
        
        for sect in records_to_recalc:
            for student in sect.student_ids:
                self.env['gestion.nota.final'].trigger_recalculate(student.id, sect.id)
        return res


class AttendanceLineHook(models.Model):
    """
    Hook que hereda gestion.attendance_line para recalcular notas finales
    cuando cambian las marcas de asistencia en sesiones confirmadas.
    """
    _inherit = 'gestion.attendance_line'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.attendance_id and rec.attendance_id.state == 'confirmed' and rec.student_id and rec.attendance_id.section_id:
                self.env['gestion.nota.final'].trigger_recalculate(rec.student_id.id, rec.attendance_id.section_id.id)
        return records

    def write(self, vals):
        old_data = {}
        if 'present' in vals or 'student_id' in vals or 'attendance_id' in vals:
            for rec in self:
                old_data[rec.id] = {
                    'student_id': rec.student_id.id,
                    'section_id': rec.attendance_id.section_id.id if (rec.attendance_id and rec.attendance_id.state == 'confirmed') else False
                }
        
        res = super().write(vals)
        
        if 'present' in vals or 'student_id' in vals or 'attendance_id' in vals:
            for rec in self:
                if rec.attendance_id and rec.attendance_id.state == 'confirmed' and rec.student_id and rec.attendance_id.section_id:
                    self.env['gestion.nota.final'].trigger_recalculate(rec.student_id.id, rec.attendance_id.section_id.id)
                old = old_data.get(rec.id)
                if old and old['student_id'] and old['section_id']:
                    new_student_id = rec.student_id.id
                    new_section_id = rec.attendance_id.section_id.id if (rec.attendance_id and rec.attendance_id.state == 'confirmed') else False
                    if old['student_id'] != new_student_id or old['section_id'] != new_section_id:
                        self.env['gestion.nota.final'].trigger_recalculate(old['student_id'], old['section_id'])
        return res

    def unlink(self):
        records_to_recalc = []
        for rec in self:
            if rec.attendance_id and rec.attendance_id.state == 'confirmed' and rec.student_id and rec.attendance_id.section_id:
                records_to_recalc.append((rec.student_id.id, rec.attendance_id.section_id.id))
        
        res = super().unlink()
        
        for student_id, section_id in records_to_recalc:
            self.env['gestion.nota.final'].trigger_recalculate(student_id, section_id)
        return res


class ParticipacionHook(models.Model):
    """
    Hook que hereda gestion.participacion.clase para recalcular notas
    finales cuando cambia la sección de una sesión de participación.
    """
    _inherit = 'gestion.participacion.clase'

    def write(self, vals):
        old_sections = {}
        if 'seccion_id' in vals:
            for rec in self:
                old_sections[rec.id] = rec.seccion_id.id
        
        res = super().write(vals)
        
        if 'seccion_id' in vals:
            for rec in self:
                if rec.seccion_id:
                    for student in rec.seccion_id.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, rec.seccion_id.id)
                old_sect_id = old_sections.get(rec.id)
                if old_sect_id and old_sect_id != rec.seccion_id.id:
                    old_sect = self.env['gestion.seccion'].browse(old_sect_id)
                    for student in old_sect.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, old_sect_id)
        return res

    def unlink(self):
        records_to_recalc = []
        for rec in self:
            if rec.seccion_id:
                records_to_recalc.append(rec.seccion_id)
        
        res = super().unlink()
        
        for sect in records_to_recalc:
            for student in sect.student_ids:
                self.env['gestion.nota.final'].trigger_recalculate(student.id, sect.id)
        return res


class ParticipacionLineHook(models.Model):
    """
    Hook que hereda gestion.participacion.line para recalcular notas
    finales cuando cambian las marcas de participación.
    """
    _inherit = 'gestion.participacion.line'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.participacion_id and rec.student_id and rec.participacion_id.seccion_id:
                self.env['gestion.nota.final'].trigger_recalculate(rec.student_id.id, rec.participacion_id.seccion_id.id)
        return records

    def write(self, vals):
        old_data = {}
        if 'participo' in vals or 'student_id' in vals or 'participacion_id' in vals:
            for rec in self:
                old_data[rec.id] = {
                    'student_id': rec.student_id.id,
                    'section_id': rec.participacion_id.seccion_id.id if rec.participacion_id else False
                }
        
        res = super().write(vals)
        
        if 'participo' in vals or 'student_id' in vals or 'participacion_id' in vals:
            for rec in self:
                if rec.participacion_id and rec.student_id and rec.participacion_id.seccion_id:
                    self.env['gestion.nota.final'].trigger_recalculate(rec.student_id.id, rec.participacion_id.seccion_id.id)
                old = old_data.get(rec.id)
                if old and old['student_id'] and old['section_id']:
                    new_student_id = rec.student_id.id
                    new_section_id = rec.participacion_id.seccion_id.id if (rec.participacion_id and rec.participacion_id.seccion_id) else False
                    if old['student_id'] != new_student_id or old['section_id'] != new_section_id:
                        self.env['gestion.nota.final'].trigger_recalculate(old['student_id'], old['section_id'])
        return res

    def unlink(self):
        records_to_recalc = []
        for rec in self:
            if rec.participacion_id and rec.student_id and rec.participacion_id.seccion_id:
                records_to_recalc.append((rec.student_id.id, rec.participacion_id.seccion_id.id))
        
        res = super().unlink()
        
        for student_id, section_id in records_to_recalc:
            self.env['gestion.nota.final'].trigger_recalculate(student_id, section_id)
        return res


class TipoEvaluacionHook(models.Model):
    """
    Hook que hereda gestion.tipo.evaluacion para recalcular notas
    cuando cambian los pesos o la sección asignada a una evaluación.
    """
    _inherit = 'gestion.tipo.evaluacion'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.seccion_id:
                for student in rec.seccion_id.student_ids:
                    self.env['gestion.nota.final'].trigger_recalculate(student.id, rec.seccion_id.id)
        return records

    def write(self, vals):
        old_sections = {}
        if 'porcentaje' in vals or 'seccion_id' in vals:
            for rec in self:
                old_sections[rec.id] = rec.seccion_id.id
        
        res = super().write(vals)
        
        if 'porcentaje' in vals or 'seccion_id' in vals:
            for rec in self:
                if rec.seccion_id:
                    for student in rec.seccion_id.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, rec.seccion_id.id)
                old_sect_id = old_sections.get(rec.id)
                if old_sect_id and old_sect_id != rec.seccion_id.id:
                    old_sect = self.env['gestion.seccion'].browse(old_sect_id)
                    for student in old_sect.student_ids:
                        self.env['gestion.nota.final'].trigger_recalculate(student.id, old_sect_id)
        return res

    def unlink(self):
        records_to_recalc = []
        for rec in self:
            if rec.seccion_id:
                records_to_recalc.append(rec.seccion_id)
        
        res = super().unlink()
        
        for sect in records_to_recalc:
            for student in sect.student_ids:
                self.env['gestion.nota.final'].trigger_recalculate(student.id, sect.id)
        return res


class SeccionHook(models.Model):
    """
    Hook que hereda gestion.seccion para sincronizar los registros
    de nota final cuando se agregan o eliminan estudiantes.
    """
    _inherit = 'gestion.seccion'

    def write(self, vals):
        res = super().write(vals)
        if 'student_ids' in vals:
            self.env['gestion.nota.final'].sudo()._ensure_nota_final_records()
            # Si un estudiante fue retirado de la sección, eliminamos su registro de nota final
            for rec in self:
                student_ids = rec.student_ids.ids
                notas_to_remove = self.env['gestion.nota.final'].sudo().search([
                    ('section_id', '=', rec.id),
                    ('student_id', 'not in', student_ids)
                ])
                if notas_to_remove:
                    notas_to_remove.unlink()
        return res
