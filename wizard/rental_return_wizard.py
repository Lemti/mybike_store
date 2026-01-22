# -*- coding: utf-8 -*-
"""
Module: Rental Return Wizard (Assistant de Retour)
Description: Assistant pour gérer le retour d'un vélo loué
Auteur: Harith Lemti & Younes Loukili
"""

from odoo import models, fields, api


class RentalReturnWizard(models.TransientModel):
    """
    Assistant de retour de vélo (Wizard/Popup).

    Ce modèle transitoire (TransientModel) est utilisé pour créer un formulaire popup
    qui guide l'utilisateur lors du retour d'un vélo loué.

    Fonctionnalités:
    - Enregistrer la date de retour réelle
    - Noter l'état du vélo au retour
    - Signaler d'éventuels dommages
    - Calculer les déductions sur la caution
    - Mettre à jour le contrat de location

    Note: Les TransientModel sont temporaires et nettoyés automatiquement par Odoo.
    """
    _name = 'mybike.rental.return.wizard'
    _description = 'Assistant Retour Location'

    # ============================================================================
    # CHAMPS PRINCIPAUX
    # ============================================================================

    contract_id = fields.Many2one(
        'mybike.rental.contract',
        string='Contrat',
        required=True,
        help='Contrat de location concerné par ce retour')

    return_date = fields.Datetime(
        string='Date Retour',
        required=True,
        default=fields.Datetime.now,
        help='Date et heure effective du retour du vélo')

    # ============================================================================
    # ÉTAT DU VÉLO
    # ============================================================================

    condition_return = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('fair', 'Correct'),
        ('poor', 'Mauvais'),
        ('damaged', 'Endommagé'),
    ], string='État du Vélo',
       required=True,
       default='good',
       help='État général du vélo au moment du retour')

    # ============================================================================
    # GESTION DES DOMMAGES
    # ============================================================================

    damage_reported = fields.Boolean(
        string='Dommage Signalé',
        default=False,
        help='Cocher si des dommages ont été constatés sur le vélo')

    damage_description = fields.Text(
        string='Description Dommages',
        help='Description détaillée des dommages constatés (rayures, casse, etc.)')

    # ============================================================================
    # DÉDUCTIONS SUR LA CAUTION
    # ============================================================================

    deposit_deduction = fields.Float(
        string='Déduction Caution (€)',
        default=0.0,
        help='Montant à déduire de la caution pour couvrir les dommages ou frais')

    deduction_reason = fields.Text(
        string='Raison Déduction',
        help='Explication de la déduction (dommages, frais de retard, etc.)')

    # ============================================================================
    # NOTES
    # ============================================================================

    notes = fields.Text(
        string='Notes',
        help='Notes additionnelles sur le retour')

    # ============================================================================
    # ACTION PRINCIPALE
    # ============================================================================

    def action_confirm_return(self):
        """
        Confirme le retour du vélo et met à jour le contrat.

        Cette méthode:
        1. Récupère toutes les informations saisies dans le wizard
        2. Met à jour le contrat de location avec ces informations
        3. Change l'état du contrat à 'returned'
        4. Ferme le wizard (popup)

        Le contrat passe alors à l'état "Retourné" et peut être clôturé
        pour générer la facture finale.

        Returns:
            dict: Action pour fermer le wizard
        """
        for wizard in self:
            # Mettre à jour le contrat avec les informations de retour
            wizard.contract_id.write({
                'actual_return_date': wizard.return_date,
                'bike_condition_return': wizard.condition_return,
                'damage_reported': wizard.damage_reported,
                'damage_description': wizard.damage_description,
                'deposit_deduction': wizard.deposit_deduction,
                'deduction_reason': wizard.deduction_reason,
                'state': 'returned',  # Passer le contrat à l'état "Retourné"
            })

        # Fermer le wizard
        return {'type': 'ir.actions.act_window_close'}
