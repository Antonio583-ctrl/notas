from odoo import http

class GestionMateria(http.Controller):
    @http.route('/gestion_materia/gestion_materia', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/gestion_materia/gestion_materia/objects', auth='public')
    def list(self, **kw):
        return http.request.render('gestion_materia.listing', {
            'root': '/gestion_materia/gestion_materia',
            'objects': http.request.env['gestion.materia'].search([]),
        })

    @http.route('/gestion_materia/gestion_materia/objects/<model("gestion.materia"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('gestion_materia.object', {
            'object': obj
        })