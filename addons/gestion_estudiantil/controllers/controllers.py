from odoo import http

class GestionEstudiantil(http.Controller):
    @http.route('/gestion_estudiantil/gestion_estudiantil', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/gestion_estudiantil/gestion_estudiantil/objects', auth='public')
    def list(self, **kw):
        return http.request.render('gestion_estudiantil.listing', {
            'root': '/gestion_estudiantil/gestion_estudiantil',
            'objects': http.request.env['gestion.estudiantil'].search([]),
        })

    @http.route('/gestion_estudiantil/gestion_estudiantil/objects/<model("gestion.estudiantil"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('gestion_estudiantil.object', {
            'object': obj
        })
