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

---

## 🔧 Configuration

### Configuration Initiale

#### 1. Créer les Produits

**Aller dans:** Ventes > Produits > Produits

**Créer des vélos de vente:**

```
Exemple 1 - Vélo de Ville
--------------------------
Nom: Giant Escape 3
Catégorie Vélo: Vélo de Ville
Peut être vendu: ✓
Prix de vente: 450 €
Marque: Giant
Taille cadre: M
Taille roues: 28 pouces
Stock: 5
```

```
Exemple 2 - Vélo Électrique
----------------------------
Nom: Specialized Turbo Vado
Catégorie Vélo: Vélo Électrique
Peut être vendu: ✓
Prix de vente: 2500 €
Marque: Specialized
Batterie: 500 Wh
Autonomie: 120 km
Stock: 3
```

**Créer des vélos de location:**

```
Exemple 1 - Location Ville
---------------------------
Nom: Vélo Ville - Location #001
Catégorie Vélo: Vélo de Ville
Disponible à la location: ✓
Prix location/heure: 5 €
Prix location/jour: 15 €
Prix location/semaine: 60 €
Prix location/mois: 200 €
Caution: 200 €
Numéro série: VL001
État location: Disponible
```

```
Exemple 2 - Location Électrique
--------------------------------
Nom: VTT Électrique - Location #E001
Catégorie Vélo: Vélo Électrique
Disponible à la location: ✓
Prix location/heure: 10 €
Prix location/jour: 35 €
Prix location/semaine: 150 €
Prix location/mois: 450 €
Caution: 500 €
Batterie: 625 Wh
État location: Disponible
```

**Créer des accessoires:**

```
Casque Adulte - 35 €
Antivol U - 45 €
Pompe portable - 15 €
Kit réparation - 20 €
Éclairage LED - 25 €
```

#### 2. Créer des Clients

**Aller dans:** Ventes > Commandes > Clients

```
Client 1
--------
Nom: Dupont Jean
Email: jean.dupont@example.com
Téléphone: +32 2 123 45 67
Adresse: Rue de la Paix 15, 1000 Bruxelles
N° Carte ID: BE1234567890
Membre fidélité: Oui
```

```
Client 2
--------
Nom: Martin Sophie
Email: sophie.martin@example.com
Téléphone: +32 2 987 65 43
Adresse: Avenue Louise 42, 1050 Bruxelles
Membre fidélité: Oui
```

#### 3. Configurer les Paramètres

**Aller dans:** Paramètres > Ventes

- Activer les variantes de produits
- Configurer les taxes (TVA 21% en Belgique)
- Définir les conditions de paiement

---

## 📖 Utilisation

### Scénario 1: Vente d'un Vélo

1. **Créer une commande**
   - Ventes > Commandes > Créer
   - Sélectionner le client
   - Ajouter des produits (vélo + accessoires)
   - Confirmer

2. **Facturer**
   - La facture est créée automatiquement
   - Enregistrer le paiement
   - Livrer le produit

3. **Sortie de stock**
   - Le stock est automatiquement mis à jour
   - Le client gagne des points fidélité

### Scénario 2: Location d'un Vélo

1. **Créer une commande de location**
   - BikeStore > Locations > Commandes > Créer
   - Sélectionner le client
   - Ajouter un vélo disponible
   - Choisir le type de location (jour/semaine/mois)
   - Définir les dates
   - Le prix est calculé automatiquement

2. **Confirmer la commande**
   - Vérifier la pièce d'identité
   - Le contrat est créé automatiquement
   - Le vélo passe en statut "Loué"

3. **Démarrer la location**
   - Encaisser la caution
   - Faire signer le contrat
   - Documenter l'état du vélo
   - Remettre le vélo au client

4. **Retour du vélo**
   - Vérifier l'état du vélo
   - Compléter les dates réelles
   - Calculer le prix final
   - Rendre la caution (avec déductions si nécessaire)

### Scénario 3: Consulter les Statistiques

1. **Reporting Ventes**
   - Ventes > Reporting > Ventes
   - Filtrer par période
   - Voir produits les plus vendus
   - Analyser les revenus

2. **Reporting Locations**
   - MyBike > Locations > Reporting
   - Taux d'occupation par vélo
   - Revenus location
   - Durée moyenne

3. **Historique Client**
   - Ouvrir fiche client
   - Onglet "Ventes" pour achats
   - Onglet "Locations" pour locations
   - Voir total dépensé et points fidélité

---

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

### Limites et Risques - Hébergement Local

⚠️ **Limites:**
- Accessible uniquement depuis l'ordinateur hôte
- Performances limitées par le matériel
- Pas de haute disponibilité
- Arrêt si l'ordinateur s'éteint

⚠️ **Risques:**
- **Sécurité**: Pas de pare-feu configuré
- **Sauvegardes**: Risque de perte de données
- **Performances**: Lenteur avec beaucoup d'utilisateurs
- **Accès distant**: Impossible sans configuration réseau

### Recommandations pour Production

Pour un déploiement réel chez le client:

1. **Hébergement Cloud**
   - OVH, AWS, DigitalOcean
   - Sauvegarde automatique
   - Haute disponibilité

2. **Sécurité**
   - HTTPS (certificat SSL)
   - Pare-feu configuré
   - Mots de passe robustes
   - Sauvegardes quotidiennes

3. **Performance**
   - Serveur dédié ou VPS
   - Au moins 4GB RAM
   - Monitoring actif

---

## 📊 Données de Démonstration

Le module inclut des données de démo pour faciliter la présentation:

### Produits
- 5 vélos de vente (ville, VTT, électrique)
- 8 vélos de location
- 10 accessoires
- 5 pièces détachées

### Clients
- 5 clients avec historique
- Différents niveaux fidélité
- Coordonnées complètes

### Commandes
- 3 ventes complétées
- 2 locations en cours
- 1 location terminée

---

## 👥 Équipe

**Harith Lemti**
- Développement backend
- Modèles de données
- Logique métier

**Younes Loukili**
- Développement frontend
- Vues et interfaces
- Tests et documentation

---

## 📝 Licence

LGPL-3

---

## 🙏 Remerciements

Merci à notre professeur pour l'encadrement de ce projet et à l'équipe Odoo pour l'excellente documentation.

---

## 📞 Contact

Pour toute question:
- harith.lemti@student.helb.be
- younes.loukili@student.helb.be

**Projet réalisé dans le cadre du cours Odoo - IODA/HELB 2024-2025**
