# -*- coding: utf-8 -*-
"""
Module: Rental Contract (Contrat de Location)
Description: Gestion complète du cycle de vie d'un contrat de location de vélo
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import models, fields, api
from odoo.exceptions import UserError


class RentalContract(models.Model):
    """
    Contrat de Location de Vélo - Modèle principal.

    Ce modèle gère le cycle de vie complet d'une location de vélo:
    1. Création du contrat (automatique depuis une commande ou manuelle)
    2. Confirmation et paiement de la caution
    3. Démarrage de la location (vélo retiré)
    4. Retour du vélo (avec assistant de retour)
    5. Clôture et facturation

    Workflow:
    draft → confirmed → ongoing → returned → closed
            (ou cancelled à tout moment sauf closed)

    Le contrat gère également:
    - Les frais supplémentaires (retard, dommages)
    - La gestion de la caution et ses déductions
    - La génération automatique de facture
    - Les statistiques de location sur le vélo
    """
    _name = 'mybike.rental.contract'
    _description = 'Contrat de Location de Vélo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Chatter + activités
    _order = 'start_date desc'

    # ============================================================================
    # INFORMATIONS PRINCIPALES
    # ============================================================================

    name = fields.Char(
        string='N° Contrat',
        required=True,
        copy=False,
        readonly=True,
        default='Nouveau',
        help='Numéro de contrat unique (auto-généré)')

    # ============================================================================
    # RELATIONS
    # ============================================================================

    order_id = fields.Many2one(
        'mybike.rental.order',
        string='Commande Source',
        ondelete='cascade',
        help='Commande de location à l\'origine de ce contrat')

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        help='Client qui loue le vélo')

    product_id = fields.Many2one(
        'product.product',
        string='Vélo',
        required=True,
        tracking=True,
        help='Vélo loué')

    # ============================================================================
    # DATES ET PÉRIODE
    # ============================================================================

    start_date = fields.Datetime(
        string='Date Début',
        required=True,
        tracking=True,
        help='Date et heure de début prévue de la location')

    end_date = fields.Datetime(
        string='Date Fin Prévue',
        required=True,
        tracking=True,
        help='Date et heure de fin prévue de la location')

    actual_return_date = fields.Datetime(
        string='Date Retour Réelle',
        readonly=True,
        tracking=True,
        help='Date et heure réelle du retour du vélo (rempli par l\'assistant)')

    # ============================================================================
    # TARIFICATION ET MONTANTS
    # ============================================================================

    rental_type = fields.Selection([
        ('hour', 'Horaire'),
        ('day', 'Journalier'),
        ('week', 'Hebdomadaire'),
        ('month', 'Mensuel'),
    ], string='Type Location',
       required=True,
       help='Type de tarification appliquée')

    unit_price = fields.Float(
        string='Prix Unitaire',
        required=True,
        help='Prix unitaire selon le type de location (€)')

    duration = fields.Float(
        string='Durée',
        compute='_compute_duration',
        store=True,
        help='Durée calculée de la location (en heures, jours, etc.)')

    subtotal = fields.Float(
        string='Sous-total',
        compute='_compute_subtotal',
        store=True,
        help='Montant de base de la location (prix × durée)')

    # ============================================================================
    # CAUTION ET FRAIS SUPPLÉMENTAIRES
    # ============================================================================

    # Caution
    deposit_amount = fields.Float(
        string='Caution',
        required=True,
        help='Montant de la caution versée par le client (€)')

    deposit_paid = fields.Boolean(
        string='Caution Payée',
        default=False,
        tracking=True,
        help='Indique si la caution a été versée')

    deposit_returned = fields.Boolean(
        string='Caution Restituée',
        default=False,
        tracking=True,
        help='Indique si la caution a été restituée au client')

    # Frais supplémentaires
    late_fee = fields.Float(
        string='Frais de Retard',
        default=0.0,
        help='Frais facturés en cas de retour tardif (€)')

    damage_fee = fields.Float(
        string='Frais Dommages',
        default=0.0,
        help='Frais pour dommages constatés sur le vélo (€)')

    additional_fees = fields.Float(
        string='Autres Frais',
        default=0.0,
        help='Autres frais divers (€)')

    # Gestion des dommages et déductions
    damage_reported = fields.Boolean(
        string='Dommage Signalé',
        default=False,
        tracking=True,
        help='Indique si des dommages ont été constatés au retour')

    damage_description = fields.Text(
        string='Description Dommages',
        help='Description détaillée des dommages constatés')

    deposit_deduction = fields.Float(
        string='Déduction Caution',
        default=0.0,
        help='Montant déduit de la caution pour dommages ou frais (€)')

    deduction_reason = fields.Text(
        string='Raison Déduction',
        help='Explication de la déduction sur la caution')

    # Montant total
    total_price = fields.Float(
        string='Total',
        compute='_compute_total_price',
        store=True,
        help='Montant total incluant tous les frais (€)')

    # ============================================================================
    # ÉTAT DU VÉLO
    # ============================================================================

    bike_condition_start = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('fair', 'Correct'),
        ('poor', 'Mauvais'),
    ], string='État Départ',
       default='excellent',
       help='État du vélo au moment du départ')

    bike_condition_return = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('fair', 'Correct'),
        ('poor', 'Mauvais'),
    ], string='État Retour',
       help='État du vélo au retour (rempli par l\'assistant)')

    condition_notes = fields.Text(
        string='Notes État',
        help='Notes sur l\'état général du vélo')

    # ============================================================================
    # WORKFLOW ET ÉTAT
    # ============================================================================

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('ongoing', 'En Cours'),
        ('returned', 'Retourné'),
        ('closed', 'Clôturé'),
        ('cancelled', 'Annulé'),
    ], string='État',
       default='draft',
       tracking=True,
       help='État actuel du contrat dans son cycle de vie')

    # ============================================================================
    # FACTURATION
    # ============================================================================

    invoice_id = fields.Many2one(
        'account.move',
        string='Facture',
        readonly=True,
        help='Facture générée pour cette location')

    invoiced = fields.Boolean(
        string='Facturé',
        default=False,
        help='Indique si une facture a été générée')

    # ============================================================================
    # MÉTHODES DE CRÉATION
    # ============================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Génère automatiquement le numéro de contrat lors de la création.

        Le numéro est généré via une séquence Odoo configurée dans
        data/sequence.xml. Format: CONT/YYYY/XXXX

        Args:
            vals_list: Liste de dictionnaires de valeurs

        Returns:
            Enregistrements créés
        """
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('mybike.rental.contract') or 'Nouveau'
        return super(RentalContract, self).create(vals_list)

    # ============================================================================
    # MÉTHODES CALCULÉES
    # ============================================================================

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """
        Calcule la durée de location selon le type de tarification.

        Conversions selon rental_type:
        - hour: différence en heures
        - day: différence en jours entiers (minimum 1)
        - week: différence en jours / 7
        - month: différence en jours / 30

        La durée est ensuite utilisée pour calculer le montant.
        """
        for contract in self:
            if contract.start_date and contract.end_date:
                delta = contract.end_date - contract.start_date
                if contract.rental_type == 'hour':
                    contract.duration = delta.total_seconds() / 3600
                elif contract.rental_type == 'day':
                    contract.duration = delta.days or 1
                elif contract.rental_type == 'week':
                    contract.duration = delta.days / 7
                elif contract.rental_type == 'month':
                    contract.duration = delta.days / 30
            else:
                contract.duration = 0

    @api.depends('unit_price', 'duration')
    def _compute_subtotal(self):
        """
        Calcule le sous-total de base de la location.

        Formule simple: prix_unitaire × durée
        Les frais supplémentaires sont ajoutés dans _compute_total_price
        """
        for contract in self:
            contract.subtotal = contract.unit_price * contract.duration

    @api.depends('subtotal', 'late_fee', 'damage_fee', 'additional_fees')
    def _compute_total_price(self):
        """
        Calcule le montant total incluant tous les frais.

        Total = sous-total + frais_retard + frais_dommages + autres_frais

        Ce montant est utilisé pour:
        - Affichage sur le contrat
        - Génération de la facture
        - Statistiques de revenus
        """
        for contract in self:
            contract.total_price = contract.subtotal + contract.late_fee + contract.damage_fee + contract.additional_fees

    # ============================================================================
    # ACTIONS WORKFLOW
    # ============================================================================

    def action_confirm(self):
        """
        Confirme le contrat.

        Vérifie que le contrat est en brouillon avant de le confirmer.
        À ce stade, le vélo n'est pas encore marqué comme loué.

        Raises:
            UserError: Si le contrat n'est pas en brouillon
        """
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Seuls les contrats en brouillon peuvent être confirmés.")

        self.write({
            'state': 'confirmed',
        })
        return True

    def action_start_rental(self):
        """
        Démarre la location (vélo retiré par le client).

        Cette méthode:
        1. Vérifie que le contrat est confirmé
        2. Vérifie que la caution a été payée
        3. Marque le vélo comme 'loué' (rental_state = 'rented')
        4. Passe le contrat à l'état 'ongoing'

        Raises:
            UserError: Si le contrat n'est pas confirmé ou si la caution n'est pas payée
        """
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError("Le contrat doit être confirmé d'abord.")

        if not self.deposit_paid:
            raise UserError("La caution doit être payée avant de retirer le vélo.")

        # Mettre le vélo en état "loué"
        product_tmpl = self.product_id.product_tmpl_id
        product_tmpl.write({
            'rental_state': 'rented',
        })

        self.write({
            'state': 'ongoing',
        })
        return True

    def action_return_bike(self):
        """
        Ouvre l'assistant de retour de vélo.

        Lance un wizard (mybike.rental.return.wizard) qui permet de:
        - Enregistrer la date de retour réelle
        - Noter l'état du vélo au retour
        - Signaler d'éventuels dommages
        - Calculer les déductions sur la caution
        - Passer le contrat à l'état 'returned'

        Returns:
            dict: Action pour ouvrir le wizard en popup

        Raises:
            UserError: Si le vélo n'est pas en location (état != ongoing)
        """
        self.ensure_one()
        if self.state != 'ongoing':
            raise UserError("Le vélo doit être en location pour être retourné.")

        return {
            'name': 'Retour de Vélo',
            'type': 'ir.actions.act_window',
            'res_model': 'mybike.rental.return.wizard',
            'view_mode': 'form',
            'target': 'new',  # Ouvre en popup
            'context': {
                'default_contract_id': self.id,
            }
        }

    def action_close_contract(self):
        """
        Clôture le contrat et génère la facture.

        Cette méthode finale du workflow:
        1. Vérifie que le vélo a été retourné
        2. Génère la facture si pas déjà facturé
        3. Remet le vélo disponible (rental_state = 'available')
        4. Met à jour les statistiques du vélo (heures louées, revenus)
        5. Passe le contrat à l'état 'closed'

        Raises:
            UserError: Si le vélo n'a pas été retourné (état != returned)
        """
        self.ensure_one()
        if self.state != 'returned':
            raise UserError("Le vélo doit être retourné avant de clôturer le contrat.")

        # Générer la facture si nécessaire
        if not self.invoiced:
            self._generate_invoice()

        # Remettre le vélo disponible
        product_tmpl = self.product_id.product_tmpl_id
        product_tmpl.write({
            'rental_state': 'available',
        })

        # Mettre à jour les statistiques du vélo
        product_tmpl.write({
            'total_rental_hours': product_tmpl.total_rental_hours + self.duration,
            'total_rental_revenue': product_tmpl.total_rental_revenue + self.total_price,
            'last_rental_date': fields.Date.today(),
        })

        self.write({
            'state': 'closed',
        })
        return True

    def action_cancel(self):
        """
        Annule le contrat.

        Peut être utilisé à tout moment sauf quand le contrat est clôturé.
        Si le vélo était en location (ongoing), le remet automatiquement disponible.

        Raises:
            UserError: Si le contrat est déjà clôturé ou annulé
        """
        self.ensure_one()
        if self.state in ('closed', 'cancelled'):
            raise UserError("Ce contrat ne peut plus être annulé.")

        # Remettre le vélo disponible si nécessaire
        if self.state == 'ongoing':
            product_tmpl = self.product_id.product_tmpl_id
            product_tmpl.write({
                'rental_state': 'available',
            })

        self.write({
            'state': 'cancelled',
        })
        return True

    # ============================================================================
    # FACTURATION
    # ============================================================================

    def _generate_invoice(self):
        """
        Génère la facture client pour la location.

        Crée une facture (account.move) avec:
        - Ligne principale: location du vélo
        - Lignes supplémentaires: frais de retard, dommages, autres

        La facture reste en brouillon, l'utilisateur doit la valider manuellement.

        Note: La caution n'apparaît pas sur la facture car elle est gérée séparément
        """
        self.ensure_one()

        # Préparer les lignes de facture
        invoice_vals = {
            'move_type': 'out_invoice',  # Facture client
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                (0, 0, {
                    'name': f'Location {self.product_id.display_name} - {self.name}',
                    'product_id': self.product_id.id,
                    'quantity': self.duration,
                    'price_unit': self.unit_price,
                }),
            ]
        }

        # Ajouter les frais de retard si applicable
        if self.late_fee > 0:
            invoice_vals['invoice_line_ids'].append(
                (0, 0, {
                    'name': 'Frais de retard',
                    'quantity': 1,
                    'price_unit': self.late_fee,
                })
            )

        # Ajouter les frais de dommages si applicable
        if self.damage_fee > 0:
            invoice_vals['invoice_line_ids'].append(
                (0, 0, {
                    'name': 'Frais de dommages',
                    'quantity': 1,
                    'price_unit': self.damage_fee,
                })
            )

        # Ajouter les frais supplémentaires si applicable
        if self.additional_fees > 0:
            invoice_vals['invoice_line_ids'].append(
                (0, 0, {
                    'name': 'Frais supplémentaires',
                    'quantity': 1,
                    'price_unit': self.additional_fees,
                })
            )

        # Créer la facture
        invoice = self.env['account.move'].create(invoice_vals)

        # Lier la facture au contrat
        self.write({
            'invoice_id': invoice.id,
            'invoiced': True,
        })

        return invoice

    def action_view_invoice(self):
        """
        Ouvre la facture associée au contrat.

        Returns:
            dict: Action pour afficher la facture dans un formulaire
        """
        self.ensure_one()
        return {
            'name': 'Facture',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }
