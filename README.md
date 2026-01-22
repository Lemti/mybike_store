# MyBike Store - Magasin de Vélos (Vente & Location)

**Projet Odoo - Examen 2025**  
**Développé par:** Harith Lemti & Younes Loukili  
**Institution:** IODA / HELB Ilya Prigogine  
**Version Odoo:** 19.0 Community

---

## 📋 Table des Matières

1. [Présentation du Projet](#présentation-du-projet)
2. [Fonctionnalités](#fonctionnalités)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Architecture Technique](#architecture-technique)
7. [Déploiement](#déploiement)

---

## 🎯 Présentation du Projet

### Contexte Client

**Bike Store** est un magasin de vélos situé à Bruxelles qui souhaite moderniser sa gestion avec un système intégré pour :
- **Vendre** des vélos neufs, pièces et accessoires
- **Louer** des vélos (courte et longue durée)
- **Gérer** efficacement son stock et sa clientèle

### Objectifs

Le client cherche une solution :
- ✅ **Abordable** : Odoo 19.0 Community (gratuit)
- ✅ **Complète** : Vente + Location dans un seul système
- ✅ **Simple** : Interface intuitive pour le personnel
- ✅ **Efficace** : Automatisation et reporting

### Besoins Métier

1. **Vente de Vélos**
   - Catalogue produits complet
   - Gestion des commandes clients
   - Facturation automatique
   - Suivi du stock en temps réel

2. **Location de Vélos**
   - Contrats de location flexibles
   - Tarification horaire, journalière, hebdomadaire, mensuelle
   - Gestion des cautions
   - Suivi de la disponibilité des vélos

3. **Gestion Clients**
   - Fiches clients détaillées
   - Historique des achats
   - Historique des locations
   - Programme de fidélité

4. **Reporting**
   - Ventes par produit/catégorie
   - Taux d'occupation des vélos de location
   - Revenus vente vs location
   - Analyse de la clientèle

---

## ⚙️ Fonctionnalités

### Module de Vente

✅ **Catalogue Produits**
- Vélos de ville, VTT, vélos de route, vélos électriques
- Pièces détachées et accessoires
- Photos et descriptions détaillées
- Gestion des stocks

✅ **Commandes Clients**
- Création de devis
- Conversion en commande
- Facturation automatique
- Suivi des paiements

✅ **Gestion du Stock**
- Entrées/sorties de stock
- Inventaire en temps réel
- Alertes stock bas
- Traçabilité complète

### Module de Location

✅ **Commandes de Location**
- Devis de location
- Sélection des vélos disponibles
- Choix de la période (heure/jour/semaine/mois)
- Calcul automatique des prix

✅ **Contrats de Location**
- Génération automatique après confirmation
- Gestion des cautions
- Documentation de l'état du vélo
- Signature électronique

✅ **Gestion de la Flotte**
- Suivi de chaque vélo (disponible/loué/maintenance)
- Historique de location par vélo
- Statistiques d'utilisation
- Planning de maintenance

### Gestion Clients

✅ **Fiches Clients**
- Informations complètes
- Vérification pièce d'identité
- Coordonnées et préférences

✅ **Historique**
- Toutes les ventes
- Toutes les locations
- Montants totaux dépensés

✅ **Programme Fidélité**
- Points de fidélité
- Niveaux (Bronze, Argent, Or, Platine)
- Réductions personnalisées

### Reporting

✅ **Tableaux de Bord**
- Vue d'ensemble activité
- Indicateurs clés (KPI)
- Graphiques interactifs

✅ **Rapports de Vente**
- Ventes par produit
- Ventes par catégorie
- Évolution temporelle

✅ **Rapports de Location**
- Taux d'occupation vélos
- Revenus location
- Durée moyenne location
- Vélos les plus loués

---

## 🚀 Installation

### Prérequis

- Python 3.10+
- PostgreSQL 12+
- Odoo 19.0 Community

### Étapes d'Installation

#### 1. Cloner le repository

```bash
git clone https://github.com/harith-lemti/mybike-store.git
cd mybike-store
```

#### 2. Installer Odoo 19.0 (si pas déjà fait)

**Option A: Installation depuis le site officiel**
```bash
wget https://nightly.odoo.com/19.0/nightly/deb/odoo_19.0.latest_all.deb
sudo dpkg -i odoo_19.0.latest_all.deb
sudo apt-get install -f
```

**Option B: Installation depuis les sources**
```bash
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0
cd odoo
pip3 install -r requirements.txt
```

#### 3. Configurer PostgreSQL

```bash
sudo -u postgres createuser -s $USER
createdb mybike_db
```

#### 4. Copier le module dans addons

```bash
# Si installation via package
sudo cp -r mybike_store /usr/lib/python3/dist-packages/odoo/addons/

# Si installation depuis sources
cp -r mybike_store /path/to/odoo/addons/
```

#### 5. Lancer Odoo

```bash
# Via service (installation package)
sudo systemctl start odoo
sudo systemctl enable odoo

# Via sources
./odoo-bin -c odoo.conf -d mybike_db --addons-path=addons,custom_addons
```

#### 6. Installer le module

1. Ouvrir http://localhost:8069
2. Se connecter (admin / admin par défaut)
3. Aller dans Apps
4. Cliquer sur "Update Apps List"
5. Rechercher "MyBike Store"
6. Cliquer sur "Install"


## 🏗️ Architecture Technique

### Structure du Module

```
mybike_store/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_template.py      # Extension produits
│   ├── rental_order.py           # Commandes location
│   ├── rental_contract.py        # Contrats location
│   └── res_partner.py            # Extension clients
├── views/
│   ├── product_template_views.xml
│   ├── rental_order_views.xml
│   ├── rental_contract_views.xml
│   ├── res_partner_views.xml
│   └── menu_views.xml
├── data/
│   ├── product_categories.xml
│   ├── rental_pricing.xml
│   └── sequence.xml
├── security/
│   └── ir.model.access.csv
├── wizard/
│   └── rental_return_wizard.py
├── report/
│   ├── rental_contract_report.xml
│   └── sales_report_views.xml
├── demo/
│   ├── demo_products.xml
│   └── demo_customers.xml
└── README.md
```

### Modèles de Données

**product.template** (héritage)
- Champs location (prix, caution, état)
- Caractéristiques vélo
- Statistiques location

**mybike.rental.order**
- Commande de location (devis)
- Lignes de commande
- Calcul prix automatique

**mybike.rental.contract**
- Contrat actif après confirmation
- Gestion caution et état vélo
- Workflow location complet

**res.partner** (héritage)
- Historique achats et locations
- Programme fidélité
- Vérification identité

### Points Techniques Clés

✅ **Héritage Odoo**: Extension de `product.template` et `res.partner`
✅ **Calculs automatiques**: Prix, durées, statistiques
✅ **Workflow complet**: États et transitions contrôlées
✅ **Contraintes de validation**: Dates, disponibilité
✅ **Reporting intégré**: Vue pivot et graphique

---

## 🌐 Déploiement

### Type d'Hébergement

**Pour ce projet: Hébergement Local**

Le système fonctionne sur un ordinateur personnel en local pour la démonstration.

### Processus d'Installation

Voir section [Installation](#installation) ci-dessus.

### Accès à l'Interface

**URL:** http://localhost:8069  
**Login:** admin  
**Password:** admin (à modifier en production)


## 📝 Licence

LGPL-3
---

## 📞 Contact

Pour toute question:
- harith.lemti@helb-prigogine.be
- younes.loukili@helb-prigogine.be

**Projet réalisé dans le cadre du cours Odoo - IODA/HELB 2024-2025**
