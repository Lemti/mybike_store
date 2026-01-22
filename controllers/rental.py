# -*- coding: utf-8 -*-
"""
Module: Rental Website Controller
Description: Contrôleur pour les pages de location de vélos (site web public)
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import http, fields
from odoo.http import request
from datetime import datetime


class MyBikeRental(http.Controller):
    """
    Contrôleur de location de vélos.

    Gère toutes les pages liées à la location sur le site web:
    - Catalogue des vélos disponibles
    - Détails d'un vélo
    - Formulaire de réservation
    - Traitement de la réservation
    - Page de confirmation
    - Espace "Mes locations"
    """

    @http.route('/rental', type='http', auth='public', website=True)
    def rental_catalog(self, bike_type=None, **kwargs):
        """
        Catalogue de vélos à louer.

        Affiche tous les vélos disponibles à la location, avec possibilité
        de filtrer par type (ville, VTT, électrique).

        Args:
            bike_type: Type de vélo pour filtrer (optionnel)
        """
        domain = [
            ('is_rental', '=', True),
            ('rental_state', '=', 'available')
        ]

        if bike_type:
            domain.append(('bike_category', '=', bike_type))

        rental_bikes = request.env['product.template'].sudo().search(domain)

        values = {
            'bikes': rental_bikes,
            'selected_type': bike_type,
            'bike_types': [
                {'id': 'city', 'name': 'Vélos de Ville'},
                {'id': 'mountain', 'name': 'VTT'},
                {'id': 'electric', 'name': 'Vélos Électriques'},
            ]
        }
        return request.render('mybike_store.rental_catalog_template', values)

    @http.route('/rental/bike/<int:bike_id>', type='http', auth='public', website=True)
    def rental_bike_detail(self, bike_id, **kwargs):
        """
        Page de détails d'un vélo de location.

        Affiche toutes les informations du vélo: caractéristiques, tarifs, etc.
        Redirige vers /rental si le vélo n'existe pas ou n'est pas disponible.
        """
        bike = request.env['product.template'].sudo().browse(bike_id)

        if not bike.exists() or not bike.is_rental:
            return request.redirect('/rental')

        values = {
            'bike': bike,
        }
        return request.render('mybike_store.rental_bike_detail_template', values)

    @http.route('/rental/booking', type='http', auth='user', website=True)
    def rental_booking_form(self, bike_id=None, **kwargs):
        """
        Formulaire de réservation de vélo.

        Affiche le formulaire pour réserver un vélo.
        Nécessite une connexion utilisateur.
        """
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/rental/booking')

        available_bikes = request.env['product.template'].sudo().search([
            ('is_rental', '=', True),
            ('rental_state', '=', 'available')
        ])

        selected_bike = None
        if bike_id:
            try:
                selected_bike = request.env['product.template'].sudo().browse(int(bike_id))
            except:
                pass

        values = {
            'bikes': available_bikes,
            'selected_bike': selected_bike,
            'partner': request.env.user.partner_id,
        }
        return request.render('mybike_store.rental_booking_form_template', values)

    @http.route('/rental/booking/submit', type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def rental_booking_submit(self, bike_id=None, rental_type=None, start_date=None, end_date=None, **kwargs):
        """
        Traitement de la réservation.

        Crée une commande de location (mybike.rental.order) avec les données
        du formulaire de réservation.

        Retourne:
            - Redirection vers la page de confirmation si succès
            - Page d'erreur si échec
        """
        try:
            # Vérifier les données obligatoires
            if not bike_id or not rental_type or not start_date or not end_date:
                raise ValueError("Tous les champs sont obligatoires")

            partner = request.env.user.partner_id

            # Créer une commande de location
            rental_order = request.env['mybike.rental.order'].sudo().create({
                'partner_id': partner.id,
                'order_date': fields.Date.today(),
            })

            # Convertir les dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

            # Trouver le product.product
            product = request.env['product.product'].sudo().search([
                ('product_tmpl_id', '=', int(bike_id))
            ], limit=1)

            if not product:
                raise ValueError("Vélo non trouvé")

            # Récupérer le prix selon le type de location
            product_tmpl = product.product_tmpl_id
            if rental_type == 'hour':
                unit_price = product_tmpl.rental_price_hour
            elif rental_type == 'day':
                unit_price = product_tmpl.rental_price_day
            elif rental_type == 'week':
                unit_price = product_tmpl.rental_price_week
            elif rental_type == 'month':
                unit_price = product_tmpl.rental_price_month
            else:
                unit_price = product_tmpl.rental_price_day

            # Créer la ligne de commande
            order_line = request.env['mybike.rental.order.line'].sudo().create({
                'order_id': rental_order.id,
                'product_id': product.id,
                'rental_type': rental_type,
                'start_date': start_dt,
                'end_date': end_dt,
                'unit_price': unit_price,
                'quantity': 1.0,
            })

            return request.redirect('/rental/booking/confirmation/%s' % rental_order.id)

        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Erreur réservation: %s" % str(e))

            return request.render('mybike_store.rental_booking_error', {
                'error': str(e)
            })

    @http.route('/rental/booking/confirmation/<int:order_id>', type='http', auth='user', website=True)
    def rental_booking_confirmation(self, order_id, **kwargs):
        """
        Page de confirmation de réservation.

        Affiche le récapitulatif de la commande de location créée.
        Vérifie que la commande appartient bien à l'utilisateur connecté.
        """
        order = request.env['mybike.rental.order'].sudo().browse(order_id)

        if not order.exists():
            return request.redirect('/rental')

        # Vérifier que c'est bien la commande de l'utilisateur
        if order.partner_id.id != request.env.user.partner_id.id:
            return request.redirect('/rental')

        values = {
            'order': order,
        }
        return request.render('mybike_store.rental_confirmation_template', values)

    @http.route('/my/rentals', type='http', auth='user', website=True)
    def my_rentals(self, **kwargs):
        """
        Espace "Mes locations".

        Affiche l'historique complet des locations de l'utilisateur:
        - Commandes de location (devis)
        - Contrats de location actifs et terminés
        """
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/my/rentals')

        partner = request.env.user.partner_id

        # Récupérer les commandes et contrats de l'utilisateur
        orders = request.env['mybike.rental.order'].sudo().search([
            ('partner_id', '=', partner.id)
        ], order='create_date desc')

        contracts = request.env['mybike.rental.contract'].sudo().search([
            ('partner_id', '=', partner.id)
        ], order='start_date desc')

        values = {
            'orders': orders,
            'contracts': contracts,
        }
        return request.render('mybike_store.my_rentals_template', values)
