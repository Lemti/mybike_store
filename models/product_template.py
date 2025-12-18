from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Catégorie de vélo
    bike_category = fields.Selection([
        ('city', 'Vélo de Ville'),
        ('mountain', 'VTT'),
        ('road', 'Vélo de Route'),
        ('electric', 'Vélo Électrique'),
        ('kids', 'Vélo Enfant'),
        ('accessory', 'Accessoire'),
    ], string='Catégorie Vélo')

    # Informations vélo
    bike_brand = fields.Char(string='Marque')
    bike_model = fields.Char(string='Modèle')
    bike_year = fields.Integer(string='Année')
    frame_size = fields.Selection([
        ('xs', 'XS (Très Petit)'),
        ('s', 'S (Petit)'),
        ('m', 'M (Moyen)'),
        ('l', 'L (Grand)'),
        ('xl', 'XL (Très Grand)'),
    ], string='Taille Cadre')
    wheel_size = fields.Integer(string='Taille Roues (pouces)')
    serial_number = fields.Char(string='Numéro de Série')

    # Caractéristiques électriques
    is_electric = fields.Boolean(string='Vélo Électrique', compute='_compute_is_electric', store=True)
    battery_capacity = fields.Integer(string='Capacité Batterie (Wh)')
    motor_power = fields.Integer(string='Puissance Moteur (W)')
    autonomy_km = fields.Integer(string='Autonomie (km)')

    # Location
    is_rental = fields.Boolean(string='Disponible à la location', default=False)
    rental_state = fields.Selection([
        ('available', 'Disponible'),
        ('rented', 'Loué'),
        ('maintenance', 'En Maintenance'),
        ('sold', 'Vendu'),
    ], string='État Location', default='available')
    
    rental_price_hour = fields.Float(string='Prix/Heure')
    rental_price_day = fields.Float(string='Prix/Jour')
    rental_price_week = fields.Float(string='Prix/Semaine')
    rental_price_month = fields.Float(string='Prix/Mois')
    rental_deposit = fields.Float(string='Caution')

    # Statistiques location
    total_rental_hours = fields.Float(string='Heures Totales Louées', readonly=True, default=0.0)
    total_rental_revenue = fields.Float(string='Revenu Total Location', readonly=True, default=0.0)
    last_rental_date = fields.Date(string='Dernière Location', readonly=True)
    maintenance_notes = fields.Text(string='Notes Maintenance')

    @api.depends('bike_category')
    def _compute_is_electric(self):
        for product in self:
            product.is_electric = product.bike_category == 'electric'

    @api.onchange('is_rental')
    def _onchange_is_rental(self):
        """Quand on active la location, désactiver la vente"""
        if self.is_rental:
            self.sale_ok = False