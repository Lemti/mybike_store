# -*- coding: utf-8 -*-
"""
Module: Product Template Extension
Description: Extension du modèle product.template pour gérer les vélos et leurs locations
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import models, fields, api


class ProductTemplate(models.Model):
    """
    Extension du modèle Odoo product.template pour ajouter des fonctionnalités
    spécifiques aux vélos et à leur location.

    Cette classe hérite de product.template et ajoute:
    - Des catégories spécifiques aux vélos
    - Des caractéristiques techniques (taille, batterie, etc.)
    - Un système de location avec tarification flexible
    - Des statistiques de location
    """
    _inherit = 'product.template'

    # ============================================================================
    # CATÉGORIE ET INFORMATIONS DE BASE
    # ============================================================================

    bike_category = fields.Selection([
        ('city', 'Vélo de Ville'),
        ('mountain', 'VTT'),
        ('road', 'Vélo de Route'),
        ('electric', 'Vélo Électrique'),
        ('kids', 'Vélo Enfant'),
        ('accessory', 'Accessoire'),
    ], string='Catégorie Vélo',
       help='Type de vélo pour faciliter la recherche et le filtrage')

    # Informations d'identification du vélo
    bike_brand = fields.Char(
        string='Marque',
        help='Marque du vélo (ex: Trek, Giant, Specialized)')

    bike_model = fields.Char(
        string='Modèle',
        help='Modèle spécifique du vélo')

    bike_year = fields.Integer(
        string='Année',
        help='Année de fabrication du vélo')

    frame_size = fields.Selection([
        ('xs', 'XS (Très Petit)'),
        ('s', 'S (Petit)'),
        ('m', 'M (Moyen)'),
        ('l', 'L (Grand)'),
        ('xl', 'XL (Très Grand)'),
    ], string='Taille Cadre',
       help='Taille du cadre pour correspondre à la morphologie du cycliste')

    wheel_size = fields.Integer(
        string='Taille Roues (pouces)',
        help='Diamètre des roues en pouces (ex: 26, 27.5, 29)')

    serial_number = fields.Char(
        string='Numéro de Série',
        help='Numéro de série unique du vélo pour identification et traçabilité')

    # ============================================================================
    # CARACTÉRISTIQUES ÉLECTRIQUES (pour vélos électriques)
    # ============================================================================

    is_electric = fields.Boolean(
        string='Vélo Électrique',
        compute='_compute_is_electric',
        store=True,
        help='Calculé automatiquement selon la catégorie du vélo')

    battery_capacity = fields.Integer(
        string='Capacité Batterie (Wh)',
        help='Capacité de la batterie en Watt-heures (ex: 500 Wh)')

    motor_power = fields.Integer(
        string='Puissance Moteur (W)',
        help='Puissance du moteur électrique en Watts (ex: 250 W)')

    autonomy_km = fields.Integer(
        string='Autonomie (km)',
        help='Distance maximale parcourable avec assistance électrique')

    # ============================================================================
    # SYSTÈME DE LOCATION
    # ============================================================================

    is_rental = fields.Boolean(
        string='Disponible à la location',
        default=False,
        help='Cocher si ce vélo peut être loué aux clients')

    rental_state = fields.Selection([
        ('available', 'Disponible'),
        ('rented', 'Loué'),
        ('maintenance', 'En Maintenance'),
        ('sold', 'Vendu'),
    ], string='État Location',
       default='available',
       help='État actuel du vélo dans le système de location')

    # Tarification flexible selon la durée de location
    rental_price_hour = fields.Float(
        string='Prix/Heure',
        help='Tarif de location à l\'heure (€)')

    rental_price_day = fields.Float(
        string='Prix/Jour',
        help='Tarif de location à la journée (€)')

    rental_price_week = fields.Float(
        string='Prix/Semaine',
        help='Tarif de location à la semaine (€)')

    rental_price_month = fields.Float(
        string='Prix/Mois',
        help='Tarif de location au mois (€)')

    rental_deposit = fields.Float(
        string='Caution',
        help='Montant de la caution à verser lors de la location (€)')

    # ============================================================================
    # STATISTIQUES ET SUIVI DE LOCATION
    # ============================================================================

    total_rental_hours = fields.Float(
        string='Heures Totales Louées',
        readonly=True,
        default=0.0,
        help='Nombre total d\'heures durant lesquelles ce vélo a été loué')

    total_rental_revenue = fields.Float(
        string='Revenu Total Location',
        readonly=True,
        default=0.0,
        help='Revenu total généré par les locations de ce vélo (€)')

    last_rental_date = fields.Date(
        string='Dernière Location',
        readonly=True,
        help='Date de la dernière location de ce vélo')

    maintenance_notes = fields.Text(
        string='Notes Maintenance',
        help='Notes sur l\'état et les interventions de maintenance')

    # ============================================================================
    # MÉTHODES CALCULÉES
    # ============================================================================

    @api.depends('bike_category')
    def _compute_is_electric(self):
        """
        Détermine automatiquement si le vélo est électrique selon sa catégorie.

        Cette méthode est déclenchée à chaque changement de bike_category et met
        à jour le champ is_electric en conséquence.
        """
        for product in self:
            product.is_electric = product.bike_category == 'electric'

    # ============================================================================
    # MÉTHODES ONCHANGE (réactions aux changements utilisateur)
    # ============================================================================

    @api.onchange('is_rental')
    def _onchange_is_rental(self):
        """
        Quand on active la location, désactive automatiquement la vente.

        Cette logique empêche qu'un même vélo soit à la fois disponible à la vente
        et à la location, ce qui pourrait créer des conflits de gestion de stock.

        Note: Cette règle peut être ajustée selon les besoins métier.
        """
        if self.is_rental:
            self.sale_ok = False
