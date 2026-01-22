# -*- coding: utf-8 -*-
"""
Module: Main Website Controller
Description: Contrôleur principal pour les pages publiques du site web
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import http
from odoo.http import request


class MyBikeWebsite(http.Controller):
    """
    Contrôleur principal du site web MyBike Store.

    Gère les pages publiques:
    - Page d'accueil
    - Page à propos
    - Page contact
    """

    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kwargs):
        """
        Page d'accueil du site.

        Affiche:
        - 6 vélos en vedette (vente)
        - 4 vélos disponibles à la location

        Returns:
            Rendu du template mybike_store.homepage
        """
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
        """
        Page à propos.

        Affiche l'histoire et les services du magasin.
        """
        return request.render('mybike_store.about_page')

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        """
        Page contact.

        Affiche le formulaire de contact et les coordonnées.
        """
        return request.render('mybike_store.contact_page')
