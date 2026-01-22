# -*- coding: utf-8 -*-
"""
Module: Partner Extension (Client)
Description: Extension du modèle res.partner pour ajouter des fonctionnalités liées aux vélos
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import models, fields, api


class ResPartner(models.Model):
    """
    Extension du modèle res.partner (Contacts/Clients).

    Ajoute des fonctionnalités spécifiques pour un magasin de vélos:
    - Statistiques d'achats et de locations
    - Informations pour location (ID, permis)
    - Programme de fidélité
    - Liste noire (blacklist) pour locations
    """
    _inherit = 'res.partner'

    # ============================================================================
    # STATISTIQUES VENTES
    # ============================================================================

    sale_order_count = fields.Integer(
        string='Nombre de Ventes',
        compute='_compute_sale_stats',
        help='Nombre total de commandes validées')

    total_sales_amount = fields.Float(
        string='Total Achats (€)',
        compute='_compute_sale_stats',
        help='Montant total dépensé en achats')

    # ============================================================================
    # STATISTIQUES LOCATIONS
    # ============================================================================

    rental_contract_count = fields.Integer(
        string='Nombre de Locations',
        compute='_compute_rental_stats',
        help='Nombre total de contrats de location')

    total_rental_amount = fields.Float(
        string='Total Locations (€)',
        compute='_compute_rental_stats',
        help='Montant total dépensé en locations')

    active_rental_count = fields.Integer(
        string='Locations en Cours',
        compute='_compute_rental_stats',
        help='Nombre de locations actuellement actives')

    # ============================================================================
    # INFORMATIONS POUR LOCATION
    # ============================================================================

    id_card_number = fields.Char(
        string='N° Carte d\'Identité',
        help='Numéro de la carte d\'identité du client')

    id_card_verified = fields.Boolean(
        string='Pièce Vérifiée',
        default=False,
        help='Indique si la pièce d\'identité a été vérifiée')

    driving_license = fields.Char(
        string='N° Permis de Conduire',
        help='Numéro du permis de conduire (pour vélos électriques rapides)')

    # ============================================================================
    # PROGRAMME FIDÉLITÉ
    # ============================================================================

    is_loyalty_member = fields.Boolean(
        string='Membre Fidélité',
        default=False,
        help='Indique si le client est inscrit au programme de fidélité')

    loyalty_points = fields.Integer(
        string='Points Fidélité',
        default=0,
        help='Nombre de points de fidélité accumulés')

    loyalty_level = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Argent'),
        ('gold', 'Or'),
        ('platinum', 'Platine'),
    ], string='Niveau Fidélité',
       compute='_compute_loyalty_level',
       store=True,
       help='Niveau calculé selon les points: Bronze(50+), Silver(200+), Gold(500+), Platinum(1000+)')

    # ============================================================================
    # PRÉFÉRENCES CLIENT
    # ============================================================================

    preferred_bike_type = fields.Selection([
        ('city', 'Vélo de Ville'),
        ('mountain', 'VTT'),
        ('road', 'Vélo de Route'),
        ('electric', 'Vélo Électrique'),
    ], string='Type de Vélo Préféré',
       help='Type de vélo préféré du client (pour recommandations)')

    # ============================================================================
    # GESTION LISTE NOIRE
    # ============================================================================

    rental_blacklist = fields.Boolean(
        string='Liste Noire Location',
        default=False,
        help='Si coché, le client ne peut plus louer de vélos')

    blacklist_reason = fields.Text(
        string='Raison Blacklist',
        help='Raison pour laquelle le client est sur la liste noire')

    # ============================================================================
    # MÉTHODES CALCULÉES - STATISTIQUES VENTES
    # ============================================================================

    def _compute_sale_stats(self):
        """
        Calcule les statistiques de vente du client.

        Parcourt toutes les commandes de vente validées (state='sale' ou 'done')
        et calcule:
        - Le nombre de commandes
        - Le montant total dépensé

        Utilisé pour afficher l'historique d'achat et identifier les bons clients.
        """
        SaleOrder = self.env['sale.order']
        for partner in self:
            # Rechercher toutes les commandes validées
            orders = SaleOrder.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done'])
            ])
            partner.sale_order_count = len(orders)
            partner.total_sales_amount = sum(orders.mapped('amount_total'))

    # ============================================================================
    # MÉTHODES CALCULÉES - STATISTIQUES LOCATIONS
    # ============================================================================

    def _compute_rental_stats(self):
        """
        Calcule les statistiques de location du client.

        Parcourt tous les contrats de location et calcule:
        - Nombre total de locations
        - Montant total dépensé (contrats terminés uniquement)
        - Nombre de locations en cours

        Permet d'identifier les clients réguliers et de suivre l'activité.
        """
        Contract = self.env['mybike.rental.contract']
        for partner in self:
            # Tous les contrats du client
            contracts = Contract.search([('partner_id', '=', partner.id)])
            partner.rental_contract_count = len(contracts)

            # Contrats terminés pour calculer le montant dépensé
            completed = contracts.filtered(lambda c: c.state in ['returned', 'closed'])
            partner.total_rental_amount = sum(completed.mapped('total_price'))

            # Contrats actifs (confirmés ou en cours)
            active = contracts.filtered(lambda c: c.state in ['confirmed', 'ongoing'])
            partner.active_rental_count = len(active)

    # ============================================================================
    # MÉTHODES CALCULÉES - PROGRAMME FIDÉLITÉ
    # ============================================================================

    @api.depends('loyalty_points')
    def _compute_loyalty_level(self):
        """
        Calcule le niveau de fidélité selon les points accumulés.

        Barème:
        - Platine: 1000+ points
        - Or: 500-999 points
        - Argent: 200-499 points
        - Bronze: 50-199 points
        - Pas de niveau: < 50 points

        Le niveau peut donner droit à des réductions ou avantages.
        """
        for partner in self:
            if partner.loyalty_points >= 1000:
                partner.loyalty_level = 'platinum'
            elif partner.loyalty_points >= 500:
                partner.loyalty_level = 'gold'
            elif partner.loyalty_points >= 200:
                partner.loyalty_level = 'silver'
            elif partner.loyalty_points >= 50:
                partner.loyalty_level = 'bronze'
            else:
                partner.loyalty_level = False

    # ============================================================================
    # ACTIONS SMART BUTTONS
    # ============================================================================

    def action_view_sales(self):
        """
        Ouvre la liste des ventes du client.

        Utilisé par un smart button sur la fiche client pour accéder rapidement
        à l'historique des achats.

        Returns:
            dict: Action pour afficher les commandes de vente
        """
        self.ensure_one()
        return {
            'name': 'Ventes Client',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_view_rentals(self):
        """
        Ouvre la liste des locations du client.

        Utilisé par un smart button sur la fiche client pour accéder rapidement
        à l'historique des locations.

        Returns:
            dict: Action pour afficher les contrats de location
        """
        self.ensure_one()
        return {
            'name': 'Locations Client',
            'type': 'ir.actions.act_window',
            'res_model': 'mybike.rental.contract',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    # ============================================================================
    # MÉTHODES UTILITAIRES - FIDÉLITÉ
    # ============================================================================

    def add_loyalty_points(self, points):
        """
        Ajoute des points de fidélité au client.

        Peut être appelée après une vente ou location pour récompenser le client.
        Le niveau de fidélité est automatiquement recalculé.

        Args:
            points (int): Nombre de points à ajouter

        Example:
            partner.add_loyalty_points(10)  # Ajoute 10 points
        """
        for partner in self:
            partner.loyalty_points += points

    # ============================================================================
    # MÉTHODES UTILITAIRES - VÉRIFICATION
    # ============================================================================

    def action_verify_id(self):
        """
        Marque la pièce d'identité comme vérifiée.

        Utilisé lors de la première location d'un client pour indiquer
        que sa carte d'identité a été contrôlée.
        """
        for partner in self:
            partner.id_card_verified = True
