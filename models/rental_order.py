# -*- coding: utf-8 -*-
"""
Module: Rental Order (Commande de Location)
Description: Gestion des commandes de location (devis) avant confirmation
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RentalOrder(models.Model):
    """
    Commande de location (quote/devis avant confirmation).

    Ce modèle gère la phase de devis pour une location de vélo.
    Une fois confirmée, la commande génère automatiquement des contrats de location
    (mybike.rental.contract) pour chaque ligne de commande.

    Workflow:
    1. draft → sent → confirmed → Création des contrats
    2. Ou draft → cancelled (annulation)
    """
    _name = 'mybike.rental.order'
    _description = 'Commande de Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Ajoute chatter et activités
    _order = 'create_date desc'

    # ============================================================================
    # INFORMATIONS PRINCIPALES
    # ============================================================================

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default='Nouveau',
        help='Référence unique de la commande (auto-générée)')

    # Informations client
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        help='Client qui effectue la réservation')

    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Téléphone',
        help='Téléphone du client (champ relatif)')

    partner_email = fields.Char(
        related='partner_id.email',
        string='Email',
        help='Email du client (champ relatif)')

    # Date de commande
    order_date = fields.Date(
        string='Date Commande',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Date de création de la commande')

    # ============================================================================
    # LIGNES DE COMMANDE
    # ============================================================================

    order_line_ids = fields.One2many(
        'mybike.rental.order.line',
        'order_id',
        string='Vélos à Louer',
        help='Liste des vélos à louer avec leurs périodes et tarifs')

    # ============================================================================
    # MONTANTS CALCULÉS
    # ============================================================================

    amount_untaxed = fields.Float(
        string='Total HT',
        compute='_compute_amounts',
        store=True,
        help='Montant total hors taxes')

    amount_tax = fields.Float(
        string='TVA',
        compute='_compute_amounts',
        store=True,
        help='Montant de la TVA (21% en Belgique)')

    amount_total = fields.Float(
        string='Total TTC',
        compute='_compute_amounts',
        store=True,
        help='Montant total toutes taxes comprises')

    total_deposit = fields.Float(
        string='Caution Totale',
        compute='_compute_amounts',
        store=True,
        help='Montant total des cautions à verser')

    # ============================================================================
    # WORKFLOW ET ÉTAT
    # ============================================================================

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Devis Envoyé'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
    ], string='État',
       default='draft',
       tracking=True,
       required=True,
       help='État actuel de la commande')

    # ============================================================================
    # NOTES
    # ============================================================================

    note = fields.Text(
        string='Conditions Générales',
        help='Conditions générales de location affichées sur le devis')

    internal_note = fields.Text(
        string='Note Interne',
        help='Note interne non visible par le client')

    # ============================================================================
    # MÉTHODES DE CRÉATION
    # ============================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Surcharge de la méthode create pour générer automatiquement la référence.

        La référence est générée via une séquence Odoo (ir.sequence) configurée
        dans data/sequence.xml. Format: LOC/YYYY/XXXX

        Args:
            vals_list: Liste de dictionnaires de valeurs pour créer les enregistrements

        Returns:
            Enregistrements créés
        """
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('mybike.rental.order') or 'Nouveau'
        return super(RentalOrder, self).create(vals_list)

    # ============================================================================
    # MÉTHODES CALCULÉES
    # ============================================================================

    @api.depends('order_line_ids.subtotal', 'order_line_ids.deposit')
    def _compute_amounts(self):
        """
        Calcule les montants totaux de la commande.

        Calculs effectués:
        - Somme des sous-totaux HT de toutes les lignes
        - TVA à 21% (taux belge)
        - Total TTC
        - Total des cautions

        Note: Déclenché automatiquement quand les lignes changent
        """
        for order in self:
            amount_untaxed = sum(order.order_line_ids.mapped('subtotal'))
            # TVA 21% en Belgique
            amount_tax = amount_untaxed * 0.21
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax
            order.total_deposit = sum(order.order_line_ids.mapped('deposit'))

    # ============================================================================
    # ACTIONS WORKFLOW
    # ============================================================================

    def action_send_quote(self):
        """
        Envoie le devis au client.

        Change l'état de la commande à 'sent' pour indiquer que le devis
        a été transmis au client. Peut être étendu pour envoyer un email.
        """
        for order in self:
            order.state = 'sent'

    def action_confirm(self):
        """
        Confirme la commande et crée les contrats de location.

        Cette méthode:
        1. Vérifie qu'il y a au moins un vélo à louer
        2. Crée un contrat de location (mybike.rental.contract) pour chaque ligne
        3. Passe la commande à l'état 'confirmed'

        Raises:
            ValidationError: Si la commande n'a pas de ligne
        """
        for order in self:
            # Validation: au moins une ligne requise
            if not order.order_line_ids:
                raise ValidationError("Vous devez ajouter au moins un vélo à louer.")

            # Créer un contrat pour chaque ligne de commande
            for line in order.order_line_ids:
                contract = self.env['mybike.rental.contract'].create({
                    'partner_id': order.partner_id.id,
                    'product_id': line.product_id.id,
                    'rental_type': line.rental_type,
                    'start_date': line.start_date,
                    'end_date': line.end_date,
                    'unit_price': line.unit_price,
                    'deposit_amount': line.deposit,
                    'order_id': order.id,
                })

            # Passer à l'état confirmé
            order.state = 'confirmed'

    def action_cancel(self):
        """
        Annule la commande.

        Simple changement d'état à 'cancelled'. Les contrats déjà créés
        (si la commande était confirmée) ne sont pas affectés.
        """
        for order in self:
            order.state = 'cancelled'

    def action_print_quote(self):
        """
        Imprime le devis PDF.

        Retourne une action pour générer et télécharger le PDF du devis.
        Le rapport doit être défini dans report/rental_quote_report.xml

        Returns:
            dict: Action pour afficher/télécharger le rapport PDF
        """
        return self.env.ref('mybike_store.action_report_rental_quote').report_action(self)


class RentalOrderLine(models.Model):
    """
    Ligne de commande de location.

    Chaque ligne représente un vélo à louer avec:
    - La période de location (dates début/fin)
    - Le type de tarification (heure, jour, semaine, mois)
    - Le prix calculé automatiquement selon la durée
    - La caution associée
    """
    _name = 'mybike.rental.order.line'
    _description = 'Ligne Commande Location'
    _order = 'order_id, sequence, id'

    # ============================================================================
    # RELATIONS
    # ============================================================================

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help='Ordre d\'affichage des lignes')

    order_id = fields.Many2one(
        'mybike.rental.order',
        string='Commande',
        required=True,
        ondelete='cascade',  # Supprime les lignes si la commande est supprimée
        help='Commande de location parente')

    # ============================================================================
    # PRODUIT (VÉLO)
    # ============================================================================

    product_id = fields.Many2one(
        'product.product',
        string='Vélo',
        required=True,
        domain="[('product_tmpl_id.is_rental', '=', True), "
               "('product_tmpl_id.rental_state', '=', 'available')]",
        help='Vélo à louer (filtré sur les vélos disponibles à la location)')

    product_name = fields.Char(
        related='product_id.name',
        string='Description',
        help='Nom du produit (champ relatif)')

    # ============================================================================
    # TYPE ET PÉRIODE DE LOCATION
    # ============================================================================

    rental_type = fields.Selection([
        ('hour', 'Par Heure'),
        ('day', 'Par Jour'),
        ('week', 'Par Semaine'),
        ('month', 'Par Mois'),
    ], string='Type Location',
       required=True,
       default='day',
       help='Type de tarification appliquée')

    start_date = fields.Datetime(
        string='Date Début',
        required=True,
        default=fields.Datetime.now,
        help='Date et heure de début de location')

    end_date = fields.Datetime(
        string='Date Fin',
        required=True,
        help='Date et heure de fin prévue de location')

    # Durées calculées automatiquement
    duration_hours = fields.Float(
        string='Durée (heures)',
        compute='_compute_duration',
        store=True,
        help='Durée en heures (calculée)')

    duration_days = fields.Float(
        string='Durée (jours)',
        compute='_compute_duration',
        store=True,
        help='Durée en jours (calculée)')

    # ============================================================================
    # PRIX ET MONTANTS
    # ============================================================================

    unit_price = fields.Float(
        string='Prix Unitaire',
        required=True,
        help='Prix unitaire selon le type de location (€)')

    quantity = fields.Float(
        string='Quantité',
        default=1.0,
        help='Quantité de vélos (généralement 1)')

    subtotal = fields.Float(
        string='Sous-total',
        compute='_compute_subtotal',
        store=True,
        help='Montant total de la ligne (calculé)')

    deposit = fields.Float(
        string='Caution',
        compute='_compute_deposit',
        store=True,
        help='Montant de la caution pour ce vélo (calculé)')

    # ============================================================================
    # NOTES
    # ============================================================================

    note = fields.Text(
        string='Note',
        help='Note spécifique à cette ligne')

    # ============================================================================
    # MÉTHODES CALCULÉES
    # ============================================================================

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """
        Calcule la durée de location en heures et en jours.

        Conversion:
        - duration_hours: différence totale en heures
        - duration_days: différence totale en jours (décimal)

        Utilisé ensuite pour calculer le prix selon le type de location.
        """
        for line in self:
            if line.start_date and line.end_date:
                delta = line.end_date - line.start_date
                line.duration_hours = delta.total_seconds() / 3600.0
                line.duration_days = delta.total_seconds() / 86400.0
            else:
                line.duration_hours = 0.0
                line.duration_days = 0.0

    @api.depends('unit_price', 'quantity', 'duration_hours', 'duration_days', 'rental_type')
    def _compute_subtotal(self):
        """
        Calcule le sous-total de la ligne selon le type de location.

        Formules de calcul:
        - hour: prix_unitaire × durée_heures × quantité
        - day: prix_unitaire × durée_jours × quantité
        - week: prix_unitaire × (durée_jours / 7) × quantité
        - month: prix_unitaire × (durée_jours / 30) × quantité

        Note: Les semaines et mois sont calculés de manière proportionnelle
        """
        for line in self:
            if line.rental_type == 'hour':
                line.subtotal = line.unit_price * line.duration_hours * line.quantity
            elif line.rental_type == 'day':
                line.subtotal = line.unit_price * line.duration_days * line.quantity
            elif line.rental_type == 'week':
                weeks = line.duration_days / 7.0
                line.subtotal = line.unit_price * weeks * line.quantity
            elif line.rental_type == 'month':
                months = line.duration_days / 30.0
                line.subtotal = line.unit_price * months * line.quantity
            else:
                line.subtotal = 0.0

    @api.depends('product_id', 'quantity')
    def _compute_deposit(self):
        """
        Calcule le montant de la caution.

        La caution est définie sur le modèle de produit (rental_deposit)
        et multipliée par la quantité de vélos loués.
        """
        for line in self:
            if line.product_id and line.product_id.product_tmpl_id.rental_deposit:
                line.deposit = line.product_id.product_tmpl_id.rental_deposit * line.quantity
            else:
                line.deposit = 0.0

    # ============================================================================
    # MÉTHODES ONCHANGE
    # ============================================================================

    @api.onchange('product_id', 'rental_type')
    def _onchange_product_rental_type(self):
        """
        Remplit automatiquement le prix unitaire selon le type de location.

        Quand l'utilisateur sélectionne un vélo et/ou change le type de location,
        cette méthode récupère automatiquement le prix correspondant depuis
        le modèle de produit (rental_price_hour, rental_price_day, etc.)

        Améliore l'expérience utilisateur en évitant la saisie manuelle des prix.
        """
        if self.product_id and self.rental_type:
            product_tmpl = self.product_id.product_tmpl_id
            if self.rental_type == 'hour':
                self.unit_price = product_tmpl.rental_price_hour
            elif self.rental_type == 'day':
                self.unit_price = product_tmpl.rental_price_day
            elif self.rental_type == 'week':
                self.unit_price = product_tmpl.rental_price_week
            elif self.rental_type == 'month':
                self.unit_price = product_tmpl.rental_price_month

    # ============================================================================
    # CONTRAINTES
    # ============================================================================

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """
        Valide que la date de fin est bien après la date de début.

        Raises:
            ValidationError: Si les dates sont invalides
        """
        for line in self:
            if line.end_date and line.start_date and line.end_date <= line.start_date:
                raise ValidationError("La date de fin doit être après la date de début.")
