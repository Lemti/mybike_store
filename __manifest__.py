{
    'name': "Bike Store - Vente & Location",
    'summary': "Gestion complète d'un magasin de vélos : vente et location",
    'description': """
        Bike Store - Magasin de Vélos
        ================================
        Module complet pour gérer un magasin de vélos offrant :
        
        Vente de vélos et accessoires :
            • Catalogue de vélos neufs (ville, VTT, route, électrique)
            • Vente de pièces détachées et accessoires
            • Gestion des commandes clients
            • Facturation automatique
            • Suivi du stock (entrées/sorties)
            
        Location de vélos :
            • Location courte durée (heure, journée)
            • Location longue durée (semaine, mois)
            • Contrats de location
            • Tarification flexible
            • Gestion de la disponibilité
            • Caution et assurance
            
        Gestion clients :
            • Fiches clients complètes
            • Historique des achats
            • Historique des locations
            • Programme de fidélité
            
        Reporting :
            • Ventes par produit/catégorie
            • Taux d'occupation des vélos de location
            • Revenus vente vs location
            • Statistiques clients
    """,
    'author': "Harith Lemti & Younes Loukili",
    'website': "https://www.mybikestore.example",
    'category': 'Sales',
    'version': '1.0.0',
    
    # Compatible Odoo 19.0 Community
    'depends': [
        'base',
        'sale_management',
        'stock',
        'product',
        'account',
        'contacts',
        'website',
        'website_sale',
    ],
    
    'data': [
        # Sécurité - Définit les droits d'accès aux modèles
        'security/ir.model.access.csv',

        # Données de base - Catégories, tarifs et séquences
        'data/product_categories.xml',
        'data/rental_pricing.xml',
        'data/sequence.xml',

        # Rapports - Chargés avant les vues pour éviter les erreurs de référence
        'report/rental_contract_report.xml',

        # Wizards - Assistants pour les actions utilisateur
        'wizard/rental_return_wizard_views.xml',

        # Vues - Interfaces utilisateur
        'views/product_template_views.xml',
        'views/rental_contract_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',

        # Website - Templates du site web public
        'views/website_templates.xml',
        'views/website_rental_templates.xml',
    ],

    # 'assets': {
    #     'web.assets_frontend': [
    #         'mybike_store/static/src/css/mybike_store.css',
    #         'mybike_store/static/src/js/rental_booking.js',
    #     ],
    # },

    'demo': [
    'demo/demo_products.xml',
    'demo/publish_products.xml',  # <-- AJOUTE CETTE LIGNE
    'demo/demo_customers.xml',
],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
