from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class RentalContract(models.Model):
    """Contrat de location actif (après confirmation)"""
    _name = 'mybike.rental.contract'
    _description = 'Contrat de Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(string='N° Contrat', required=True, copy=False, 
                       readonly=True, default='Nouveau')
    
    # Référence commande
    rental_order_id = fields.Many2one('mybike.rental.order', string='Commande Origine')
    
    # Client
    partner_id = fields.Many2one('res.partner', string='Client', 
                                  required=True, tracking=True, index=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Téléphone')
    partner_email = fields.Char(related='partner_id.email', string='Email')
    
    # Vélo loué
    product_id = fields.Many2one('product.product', string='Vélo Loué', 
                                  required=True, tracking=True,
                                  domain="[('product_tmpl_id.is_rental', '=', True)]")
    serial_number = fields.Char(related='product_id.product_tmpl_id.serial_number', 
                                 string='N° Série')
    
    # Période de location
    rental_type = fields.Selection([
        ('hour', 'Par Heure'),
        ('day', 'Par Jour'),
        ('week', 'Par Semaine'),
        ('month', 'Par Mois'),
    ], string='Type Location', required=True, tracking=True)
    
    start_date = fields.Datetime(string='Date Début', required=True, 
                                  default=fields.Datetime.now, tracking=True)
    end_date = fields.Datetime(string='Date Fin Prévue', required=True, tracking=True)
    actual_return_date = fields.Datetime(string='Date Retour Réelle', tracking=True)
    
    duration_hours = fields.Float(string='Durée (heures)', 
                                   compute='_compute_duration', store=True)
    duration_days = fields.Float(string='Durée (jours)', 
                                  compute='_compute_duration', store=True)
    
    # Tarification
    unit_price = fields.Float(string='Prix Unitaire', required=True)
    total_price = fields.Float(string='Prix Total', compute='_compute_total_price', store=True)
    
    # Caution
    deposit = fields.Float(string='Caution Versée (€)', required=True)
    deposit_paid = fields.Boolean(string='Caution Payée', default=False, tracking=True)
    deposit_returned = fields.Boolean(string='Caution Rendue', default=False, tracking=True)
    deposit_deduction = fields.Float(string='Déduction Caution (€)', default=0.0)
    deduction_reason = fields.Text(string='Raison Déduction')
    
    # État du vélo
    condition_start = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('fair', 'Correct'),
        ('poor', 'Mauvais'),
    ], string='État au Départ', default='good')
    
    condition_return = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('fair', 'Correct'),
        ('poor', 'Mauvais'),
        ('damaged', 'Endommagé'),
    ], string='État au Retour')
    
    damage_reported = fields.Boolean(string='Dommage Signalé', default=False)
    damage_description = fields.Text(string='Description Dommages')
    
    # État du contrat
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('ongoing', 'En Cours'),
        ('returned', 'Retourné'),
        ('closed', 'Clôturé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', required=True, tracking=True)
    
    # Assurance optionnelle
    insurance = fields.Boolean(string='Assurance Souscrite', default=False)
    insurance_price = fields.Float(string='Prix Assurance (€)', default=5.0)
    
    # Paiement
    payment_status = fields.Selection([
        ('unpaid', 'Non Payé'),
        ('partial', 'Partiel'),
        ('paid', 'Payé'),
    ], string='Statut Paiement', default='unpaid', tracking=True)
    
    # Documents
    contract_signed = fields.Boolean(string='Contrat Signé', default=False)
    id_verified = fields.Boolean(string='Pièce d\'Identité Vérifiée', default=False)
    
    # Notes
    note = fields.Text(string='Notes')
    internal_note = fields.Text(string='Note Interne')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('mybike.rental.contract') or 'Nouveau'
        return super(RentalContract, self).create(vals)
    
    @api.depends('start_date', 'end_date', 'actual_return_date')
    def _compute_duration(self):
        for contract in self:
            end = contract.actual_return_date if contract.actual_return_date else contract.end_date
            if contract.start_date and end:
                delta = end - contract.start_date
                contract.duration_hours = delta.total_seconds() / 3600.0
                contract.duration_days = delta.total_seconds() / 86400.0
            else:
                contract.duration_hours = 0.0
                contract.duration_days = 0.0
    
    @api.depends('unit_price', 'duration_hours', 'duration_days', 'rental_type', 'insurance', 'insurance_price')
    def _compute_total_price(self):
        for contract in self:
            base_price = 0.0
            
            if contract.rental_type == 'hour':
                base_price = contract.unit_price * contract.duration_hours
            elif contract.rental_type == 'day':
                base_price = contract.unit_price * contract.duration_days
            elif contract.rental_type == 'week':
                weeks = contract.duration_days / 7.0
                base_price = contract.unit_price * weeks
            elif contract.rental_type == 'month':
                months = contract.duration_days / 30.0
                base_price = contract.unit_price * months
            
            # Ajouter l'assurance si souscrite
            if contract.insurance:
                base_price += contract.insurance_price
            
            contract.total_price = base_price
    
    def action_confirm(self):
        """Confirme le contrat"""
        for contract in self:
            if not contract.id_verified:
                raise UserError("Veuillez vérifier la pièce d'identité du client.")
            if not contract.deposit_paid:
                raise UserError("La caution doit être payée avant de confirmer le contrat.")
            
            contract.state = 'confirmed'
            # Marque le vélo comme loué
            contract.product_id.product_tmpl_id.rental_state = 'rented'
    
    def action_start_rental(self):
        """Démarre la location (vélo remis au client)"""
        for contract in self:
            if not contract.contract_signed:
                raise UserError("Le contrat doit être signé avant de démarrer la location.")
            
            contract.write({
                'state': 'ongoing',
                'start_date': fields.Datetime.now()
            })
    
    def action_return_bike(self):
        """Traite le retour du vélo"""
        for contract in self:
            if contract.state != 'ongoing':
                raise UserError("Seules les locations en cours peuvent être retournées.")
            
            # Ouvre un wizard pour documenter le retour
            return {
                'name': 'Retour du Vélo',
                'type': 'ir.actions.act_window',
                'res_model': 'mybike.rental.return.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_contract_id': contract.id,
                    'default_return_date': fields.Datetime.now()
                }
            }
    
    def action_close_contract(self):
        """Clôture le contrat après retour"""
        for contract in self:
            if contract.state != 'returned':
                raise UserError("Le vélo doit être retourné avant de clôturer le contrat.")
            
            # Calcule les déductions éventuelles
            if contract.damage_reported and contract.deposit_deduction == 0:
                raise UserError("Veuillez indiquer le montant à déduire de la caution.")
            
            contract.state = 'closed'
            
            # Rend le vélo disponible ou l'envoie en maintenance
            if contract.condition_return in ['excellent', 'good']:
                contract.product_id.product_tmpl_id.rental_state = 'available'
            else:
                contract.product_id.product_tmpl_id.rental_state = 'maintenance'
    
    def action_return_deposit(self):
        """Rend la caution au client"""
        for contract in self:
            if contract.state != 'closed':
                raise UserError("Le contrat doit être clôturé avant de rendre la caution.")
            
            amount_to_return = contract.deposit - contract.deposit_deduction
            
            # TODO: Créer un remboursement dans la comptabilité
            
            contract.deposit_returned = True
    
    def action_cancel(self):
        """Annule le contrat"""
        for contract in self:
            if contract.state in ['ongoing', 'returned']:
                raise UserError("Impossible d'annuler un contrat en cours ou retourné.")
            
            contract.state = 'cancelled'
            # Libère le vélo
            if contract.product_id.product_tmpl_id.rental_state == 'rented':
                contract.product_id.product_tmpl_id.rental_state = 'available'
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for contract in self:
            if contract.end_date and contract.start_date and contract.end_date <= contract.start_date:
                raise ValidationError("La date de fin doit être après la date de début.")
    
    def action_print_contract(self):
        """Imprime le contrat de location"""
        return self.env.ref('mybike_store.action_report_rental_contract').report_action(self)
