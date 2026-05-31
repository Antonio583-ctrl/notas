# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import base64

# class GestionProfesorado(http.Controller):
#     @http.route('/gestion_profesorado/gestion_profesorado', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestion_profesorado/gestion_profesorado/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestion_profesorado.listing', {
#             'root': '/gestion_profesorado/gestion_profesorado',
#             'objects': http.request.env['gestion_profesorado.profesor'].search([]),
#         })

#     @http.route('/gestion_profesorado/gestion_profesorado/objects/<model("gestion_profesorado.profesor"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestion_profesorado.object', {
#             'object': obj
###         })
##class GestionProfesorado(http.Controller):
##
##    @http.route('/gestion/actividad/<model("gestion.activity"):activity>', type='http', auth="user", website=True)
##    def actividad_detalle(self, activity, **kw):
##        return request.render('gestion_estudiantil.portal_actividad_page', {
##            'activity': activity,
##        })
##
##    
##    @http.route('/gestion/actividad/subir', type='http', auth="user", methods=['POST'], website=True)
##    def subir_entrega(self, activity_id, archivo_tarea, **kw):
##        if archivo_tarea:
##            # Leer el archivo y convertirlo a base64 (como lo requiere el campo Binary de Odoo)
##            file_content = archivo_tarea.read()
##            file_name = archivo_tarea.filename
##            
##            
##            nueva_entrega = request.env['gestion.submission'].sudo().create({
##                'activity_id': int(activity_id),
##                'student_id': request.env.user.partner_id.id, 
##                'file_data': base64.b64encode(file_content),
##                'file_name': file_name,
##            })
##            
##            
##            return request.redirect(f'/gestion/actividad/{activity_id}?success=1')
##        
##        return request.redirect('/my/home')
##