from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RentalOrder(models.Model):
    """Commande de location (quote avant confirmation)"""
    _name = 'mybike.rental.order'
    _description = 'Commande de Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Référence', required=True, copy=False, 
                       readonly=True, default='Nouveau')
    
    # Client
    partner_id = fields.Many2one('res.partner', string='Client', 
                                  required=True, tracking=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Téléphone')
    partner_email = fields.Char(related='partner_id.email', string='Email')
    
    # Date de commande
    order_date = fields.Date(string='Date Commande', required=True, 
                             default=fields.Date.today, tracking=True)
    
    # Lignes de commande
    order_line_ids = fields.One2many('mybike.rental.order.line', 'order_id', 
                                      string='Vélos à Louer')
    
    # Montants
    amount_untaxed = fields.Float(string='Total HT', compute='_compute_amounts', store=True)
    amount_tax = fields.Float(string='TVA', compute='_compute_amounts', store=True)
    amount_total = fields.Float(string='Total TTC', compute='_compute_amounts', store=True)
    total_deposit = fields.Float(string='Caution Totale', compute='_compute_amounts', store=True)
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Devis Envoyé'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True, required=True)
    
    # Notes
    note = fields.Text(string='Conditions Générales')
    internal_note = fields.Text(string='Note Interne')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('mybike.rental.order') or 'Nouveau'
        return super(RentalOrder, self).create(vals)
    
    @api.depends('order_line_ids.subtotal', 'order_line_ids.deposit')
    def _compute_amounts(self):
        for order in self:
            amount_untaxed = sum(order.order_line_ids.mapped('subtotal'))
            # TVA 21% en Belgique
            amount_tax = amount_untaxed * 0.21
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax
            order.total_deposit = sum(order.order_line_ids.mapped('deposit'))
    
    def action_send_quote(self):
        """Envoie le devis au client"""
        for order in self:
            order.state = 'sent'
    
    def action_confirm(self):
        """Confirme la commande et crée les contrats de location"""
        for order in self:
            if not order.order_line_ids:
                raise ValidationError("Vous devez ajouter au moins un vélo à louer.")
            
            # Créer un contrat pour chaque ligne
            for line in order.order_line_ids:
                contract = self.env['mybike.rental.contract'].create({
                    'partner_id': order.partner_id.id,
                    'product_id': line.product_id.id,
                    'rental_type': line.rental_type,
                    'start_date': line.start_date,
                    'end_date': line.end_date,
                    'unit_price': line.unit_price,
                    'deposit': line.deposit,
                    'rental_order_id': order.id,
                })
            
            order.state = 'confirmed'
    
    def action_cancel(self):
        """Annule la commande"""
        for order in self:
            order.state = 'cancelled'
    
    def action_print_quote(self):
        """Imprime le devis"""
        return self.env.ref('mybike_store.action_report_rental_quote').report_action(self)


class RentalOrderLine(models.Model):
    """Ligne de commande de location"""
    _name = 'mybike.rental.order.line'
    _description = 'Ligne Commande Location'
    _order = 'order_id, sequence, id'

    sequence = fields.Integer(string='Séquence', default=10)
    order_id = fields.Many2one('mybike.rental.order', string='Commande', 
                                required=True, ondelete='cascade')
    
    # Produit
    product_id = fields.Many2one('product.product', string='Vélo', 
                                  required=True,
                                  domain="[('product_tmpl_id.is_rental', '=', True), "
                                         "('product_tmpl_id.rental_state', '=', 'available')]")
    product_name = fields.Char(related='product_id.name', string='Description')
    
    # Type et période de location
    rental_type = fields.Selection([
        ('hour', 'Par Heure'),
        ('day', 'Par Jour'),
        ('week', 'Par Semaine'),
        ('month', 'Par Mois'),
    ], string='Type Location', required=True, default='day')
    
    start_date = fields.Datetime(string='Date Début', required=True, 
                                  default=fields.Datetime.now)
    end_date = fields.Datetime(string='Date Fin', required=True)
    
    duration_hours = fields.Float(string='Durée (heures)', 
                                   compute='_compute_duration', store=True)
    duration_days = fields.Float(string='Durée (jours)', 
                                  compute='_compute_duration', store=True)
    
    # Prix
    unit_price = fields.Float(string='Prix Unitaire', required=True)
    quantity = fields.Float(string='Quantité', default=1.0)
    subtotal = fields.Float(string='Sous-total', compute='_compute_subtotal', store=True)
    deposit = fields.Float(string='Caution', compute='_compute_deposit', store=True)
    
    # Notes
    note = fields.Text(string='Note')
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
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
        for line in self:
            if line.product_id and line.product_id.product_tmpl_id.rental_deposit:
                line.deposit = line.product_id.product_tmpl_id.rental_deposit * line.quantity
            else:
                line.deposit = 0.0
    
    @api.onchange('product_id', 'rental_type')
    def _onchange_product_rental_type(self):
        """Remplit automatiquement le prix selon le type de location"""
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
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for line in self:
            if line.end_date and line.start_date and line.end_date <= line.start_date:
                raise ValidationError("La date de fin doit être après la date de début.")
