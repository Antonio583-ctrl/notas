# -*- coding: utf-8 -*-
import base64 
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class EstudiantePortal(CustomerPortal):

    # 1. RUTA PARA MATERIAS (Desde Secciones)
    @http.route(['/my/subjects'], type='http', auth="user", website=True)
    def portal_my_subjects(self, **kw):
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id
        
        # Buscamos el estudiante y lo usamos en el domain
        student = request.env['gestion.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        
        secciones = request.env['gestion.seccion'].sudo().search([
            ('student_ids', 'in', student.id if student else 0)
        ])
        
        return request.render("gestion_estudiantil.portal_my_subjects_template", {
            'secciones': secciones, 
            'page_name': 'materias',
        })

    # 2. RUTA PARA ACTIVIDADES
    @http.route(['/my/activities'], type='http', auth="user", website=True)
    def portal_my_activities(self, search='', subject_filter=None, section_filter=None, **kw):
        partner_id = request.env.user.partner_id.id
        student = request.env['gestion.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        
        # 1. Base del dominio
        domain = [('section_id.student_ids', 'in', student.id if student else 0)]
        
        if search:
            domain += [('name', 'ilike', search)]
        
        try:
            sub_id = int(subject_filter) if subject_filter else 0
        except ValueError:
            sub_id = 0
            
        try:
            sec_id = int(section_filter) if section_filter else 0
        except ValueError:
            sec_id = 0

        # 2. Lógica de Choque de Filtros
        if sub_id:
            domain += [('subject_id', '=', sub_id)]
            # Si eligió una materia, verificamos que la sección seleccionada pertenezca a esa materia
            if sec_id:
                check_sec = request.env['gestion.seccion'].sudo().browse(sec_id)
                # Si la sección es de otra materia, ignoramos el filtro de sección
                if check_sec.exists() and check_sec.subject_id.id != sub_id:
                    sec_id = 0 

        if sec_id:
            domain += [('section_id', '=', sec_id)]
            
        actividades = request.env['gestion.activity'].sudo().search(domain)
        
        # 3. Datos para los selectores web
        all_secciones = request.env['gestion.seccion'].sudo().search([
            ('student_ids', 'in', student.id if student else 0)
        ])
        materias_alumno = all_secciones.mapped('subject_id')

        # Si hay materia seleccionada, solo enviamos las secciones de ESA materia al portal
        if sub_id:
            secciones_para_filtro = all_secciones.filtered(lambda s: s.subject_id.id == sub_id)
        else:
            secciones_para_filtro = all_secciones

        return request.render("gestion_estudiantil.portal_my_activities_template", {
            'actividades': actividades,
            'materias': materias_alumno,
            'secciones': secciones_para_filtro,
            'search': search,
            'subject_filter': sub_id,
            'section_filter': sec_id,
            'page_name': 'actividades',
        })

    @http.route(['/my/activities/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_activity_detail(self, activity_id, **kw):
        activity = request.env['gestion.activity'].sudo().browse(activity_id)
        
        if not activity.exists():
            return request.not_found()

        return request.render("gestion_estudiantil.portal_actividad_page", {
            'activity': activity,
            'page_name': 'actividad_detalle',
        })
    
    @http.route(['/gestion/actividad/subir'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def portal_submit_activity(self, **post):
        activity_id = int(post.get('activity_id'))
        archivo = post.get('archivo_tarea')
        
        partner_id = request.env.user.partner_id.id
        # Buscamos al estudiante real para asignarle la tarea
        student = request.env['gestion.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)

        if archivo and student:
            file_content = base64.b64encode(archivo.read())
            file_name = archivo.filename

            # Usamos student.id en la creación
            request.env['gestion.submission'].sudo().create({
                'activity_id': activity_id,
                'student_id': student.id,
                'file_data': file_content,
                'file_name': file_name,
            })

        return request.redirect(f'/my/activities/{activity_id}?success=1')

    # 3. RUTA PARA NOTAS (Modelo grade.grade)
    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw):
        values = self._prepare_portal_layout_values()
        user_name = request.env.user.name
        
        # Dejado igual, asumiendo que el ilike por nombre sigue funcionando con la herencia
        notas = request.env['grade.grade'].sudo().search([
            ('student_id.name', 'ilike', user_name)
        ])
        
        return request.render("gestion_estudiantil.portal_my_grades_template", {
            'notas': notas,
            'page_name': 'notas',
        })

    # 4. RUTA PARA AUSENCIAS (Asistencias)
    @http.route(['/my/absences'], type='http', auth="user", website=True)
    def portal_my_absences(self, **kw):
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id
        
        student = request.env['gestion.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        
        asistencias = request.env['gestion.attendance_line'].sudo().search([
            ('student_id', '=', student.id if student else 0)
        ])
        
        return request.render("gestion_estudiantil.portal_my_absences_template", {
            'asistencias': asistencias,
            'page_name': 'ausencias',
        })

    # 5. RUTA PARA SECCIONES
    @http.route(['/my/sections'], type='http', auth="user", website=True)
    def portal_my_sections(self, **kw):
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id
        
        student = request.env['gestion.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        
        secciones = request.env['gestion.seccion'].sudo().search([
            ('student_ids', 'in', student.id if student else 0)
        ])
        
        return request.render("gestion_estudiantil.portal_my_sections_template", {
            'secciones': secciones,
            'page_name': 'secciones',
        })

    # 6. RUTA PARA PROFESORES
    @http.route(['/my/teachers'], type='http', auth="user", website=True)
    def portal_my_teachers(self, **kw):
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id.id
        
        student = request.env['gestion.student'].sudo().search([('partner_id', '=', partner_id)], limit=1)
        
        secciones = request.env['gestion.seccion'].sudo().search([
            ('student_ids', 'in', student.id if student else 0)
        ])
        profesores = secciones.mapped('teacher_id')
        
        return request.render("gestion_estudiantil.portal_my_teachers_template", {
            'profesores': profesores,
            'page_name': 'profesores',
        })