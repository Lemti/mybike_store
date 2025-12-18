from odoo import http
from odoo.http import request


class MyBikeWebsite(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kwargs):
        """Page d'accueil du site"""
        # Récupérer les vélos en vedette pour la vente
        featured_bikes = request.env['product.template'].sudo().search([
            ('bike_category', 'in', ['electric', 'mountain', 'city']),
            ('sale_ok', '=', True),
        ], limit=6)
        
        # Récupérer les vélos de location disponibles
        rental_bikes = request.env['product.template'].sudo().search([
            ('is_rental', '=', True),
            ('rental_state', '=', 'available')
        ], limit=4)
        
        values = {
            'featured_bikes': featured_bikes,
            'rental_bikes': rental_bikes,
        }
        return request.render('mybike_store.homepage', values)

    @http.route('/about', type='http', auth='public', website=True)
    def about(self, **kwargs):
        """Page à propos"""
        return request.render('mybike_store.about_page')

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        """Page contact"""
        return request.render('mybike_store.contact_page')