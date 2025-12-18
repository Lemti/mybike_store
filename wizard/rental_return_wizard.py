from odoo import models, fields, api


class RentalReturnWizard(models.TransientModel):
    _name = 'mybike.rental.return.wizard'
    _description = 'Assistant Retour Location'

    contract_id = fields.Many2one('mybike.rental.contract', string='Contrat', required=True)
    return_date = fields.Datetime(string='Date Retour', required=True, default=fields.Datetime.now)
    
    condition_return = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('fair', 'Correct'),
        ('poor', 'Mauvais'),
        ('damaged', 'Endommagé'),
    ], string='État du Vélo', required=True, default='good')
    
    damage_reported = fields.Boolean(string='Dommage Signalé', default=False)
    damage_description = fields.Text(string='Description Dommages')
    deposit_deduction = fields.Float(string='Déduction Caution (€)', default=0.0)
    deduction_reason = fields.Text(string='Raison Déduction')
    
    notes = fields.Text(string='Notes')
    
    def action_confirm_return(self):
        """Confirme le retour du vélo"""
        for wizard in self:
            wizard.contract_id.write({
                'actual_return_date': wizard.return_date,
                'condition_return': wizard.condition_return,
                'damage_reported': wizard.damage_reported,
                'damage_description': wizard.damage_description,
                'deposit_deduction': wizard.deposit_deduction,
                'deduction_reason': wizard.deduction_reason,
                'state': 'returned',
            })
        
        return {'type': 'ir.actions.act_window_close'}
