from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Historique achats
    sale_order_count = fields.Integer(string='Nombre de Ventes', 
                                        compute='_compute_sale_stats')
    total_sales_amount = fields.Float(string='Total Achats (€)', 
                                       compute='_compute_sale_stats')
    
    # Historique locations
    rental_contract_count = fields.Integer(string='Nombre de Locations', 
                                            compute='_compute_rental_stats')
    total_rental_amount = fields.Float(string='Total Locations (€)', 
                                        compute='_compute_rental_stats')
    active_rental_count = fields.Integer(string='Locations en Cours', 
                                          compute='_compute_rental_stats')
    
    # Informations complémentaires pour location
    id_card_number = fields.Char(string='N° Carte d\'Identité')
    id_card_verified = fields.Boolean(string='Pièce Vérifiée', default=False)
    driving_license = fields.Char(string='N° Permis de Conduire')
    
    # Programme fidélité
    is_loyalty_member = fields.Boolean(string='Membre Fidélité', default=False)
    loyalty_points = fields.Integer(string='Points Fidélité', default=0)
    loyalty_level = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Argent'),
        ('gold', 'Or'),
        ('platinum', 'Platine'),
    ], string='Niveau Fidélité', compute='_compute_loyalty_level', store=True)
    
    # Préférences
    preferred_bike_type = fields.Selection([
        ('city', 'Vélo de Ville'),
        ('mountain', 'VTT'),
        ('road', 'Vélo de Route'),
        ('electric', 'Vélo Électrique'),
    ], string='Type de Vélo Préféré')
    
    # Blacklist
    rental_blacklist = fields.Boolean(string='Liste Noire Location', default=False)
    blacklist_reason = fields.Text(string='Raison Blacklist')
    
    def _compute_sale_stats(self):
        """Calcule les statistiques de vente"""
        SaleOrder = self.env['sale.order']
        for partner in self:
            orders = SaleOrder.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done'])
            ])
            partner.sale_order_count = len(orders)
            partner.total_sales_amount = sum(orders.mapped('amount_total'))
    
    def _compute_rental_stats(self):
        """Calcule les statistiques de location"""
        Contract = self.env['mybike.rental.contract']
        for partner in self:
            contracts = Contract.search([('partner_id', '=', partner.id)])
            partner.rental_contract_count = len(contracts)
            
            completed = contracts.filtered(lambda c: c.state in ['returned', 'closed'])
            partner.total_rental_amount = sum(completed.mapped('total_price'))
            
            active = contracts.filtered(lambda c: c.state in ['confirmed', 'ongoing'])
            partner.active_rental_count = len(active)
    
    @api.depends('loyalty_points')
    def _compute_loyalty_level(self):
        """Calcule le niveau de fidélité selon les points"""
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
    
    def action_view_sales(self):
        """Affiche les ventes du client"""
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
        """Affiche les locations du client"""
        self.ensure_one()
        return {
            'name': 'Locations Client',
            'type': 'ir.actions.act_window',
            'res_model': 'mybike.rental.contract',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
    
    def add_loyalty_points(self, points):
        """Ajoute des points fidélité"""
        for partner in self:
            partner.loyalty_points += points
    
    def action_verify_id(self):
        """Marque la pièce d'identité comme vérifiée"""
        for partner in self:
            partner.id_card_verified = True
