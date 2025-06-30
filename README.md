# 🏪 StockManager Pro - Système de Gestion de Stock Intelligent

## 📋 Vue d'ensemble

**StockManager Pro** est une solution complète de gestion de stock et de facturation développée avec Django. Notre plateforme offre trois niveaux d'abonnement adaptés à tous types d'entreprises, des petits commerçants aux grandes entreprises.

## 🎯 Nos Offres d'Abonnement

### 💚 Plan Gratuit - 0 GNF
**Idéal pour les petits vendeurs ou commerçants débutants**

✅ **Fonctionnalités incluses :**
- Gestion simple du stock (ajout, sortie, alerte)
- Enregistrement des ventes quotidiennes
- Historique des opérations
- Alertes de stock minimum
- Interface mobile responsive
- Support communautaire par WhatsApp
- 1 seul utilisateur
- 1 seule boutique
- Jusqu'à 100 produits
- 10 factures par mois

### 🔥 Plan Complet - 80 000 GNF/mois
**Pour les commerces structurés : boutiques, librairies, points de vente**

✅ **Toutes les fonctionnalités Gratuit +**
- Multi-utilisateur (jusqu'à 3)
- Statistiques simplifiées (ventes, produits, charges)
- Gestion des flux financiers (entrées/sorties, bénéfices)
- Génération de factures PDF professionnelles
- Envoi d'email automatique aux clients
- Sauvegarde cloud et sécurité renforcée
- Support standard
- Jusqu'à 1000 produits
- 100 factures par mois
- Rapports avancés

### 💎 Plan Premium - 200 000 GNF/mois
**Pour les gestionnaires, franchises, pharmacies, salons, garagistes**

✅ **Toutes les fonctionnalités Complet +**
- Nombre illimité de boutiques
- Gestion multi-utilisateurs illimitée
- Gestion avancée du stock (FIFO, historiques)
- Comptabilité simplifiée (charges, rentabilité)
- Modules personnalisés selon activité
- Exports CSV, sauvegarde automatique
- **🤖 Accès à l'IA (assistant + prévision ventes)**
- Support prioritaire 24h/24
- Produits illimités
- Factures illimitées
- Accès API complet

## 🚀 Fonctionnalités Principales

### 📦 Gestion de Stock Intelligente
- ✅ Suivi en temps réel de tous vos produits
- ✅ Alertes automatiques pour les stocks faibles
- ✅ Gestion des entrées et sorties de marchandises
- ✅ Historique complet des mouvements de stock
- ✅ Gestion des catégories et sous-catégories
- ✅ Codes-barres et identification produits
- ✅ Scanner de codes-barres intégré
- ✅ Génération automatique de codes-barres

### 💼 Facturation Professionnelle
- ✅ Génération automatique de factures PDF
- ✅ Numérotation automatique des factures
- ✅ Modèles personnalisables avec logo d'entreprise
- ✅ Envoi direct par email aux clients
- ✅ Suivi des paiements et historique
- ✅ Impression directe depuis l'application
- ✅ Gestion des clients et fournisseurs

### 📊 Tableaux de Bord et Analyses
- ✅ Graphiques de ventes et évolution du chiffre d'affaires
- ✅ Statistiques des produits les plus vendus
- ✅ Analyse des bénéfices et charges
- ✅ Rapports de performance par période
- ✅ Alertes de stock et ruptures automatiques
- ✅ Exportation des données au format CSV/Excel

### 🤖 Intelligence Artificielle (Plan Premium)
- ✅ Prédictions de ventes basées sur l'historique
- ✅ Recommandations de réapprovisionnement
- ✅ Détection automatique des tendances de vente
- ✅ Optimisation des niveaux de stock minimum
- ✅ Analyse prédictive des meilleures périodes
- ✅ Assistant intelligent pour la prise de décision

## 💳 Méthodes de Paiement

Nous acceptons plusieurs moyens de paiement pour votre convenance :

- **💳 Lengo Pay** - Paiement sécurisé en ligne
- **📱 Mobile Money** - Orange Money, MTN Money
- **🏦 Virement bancaire** - Transfert bancaire direct

## 🛠️ Technologies Utilisées

### Backend
- **Django 4.2** - Framework web Python
- **Django REST Framework** - API REST
- **MySQL/SQLite** - Base de données
- **Celery** - Tâches asynchrones
- **Redis** - Cache et broker de messages

### Frontend
- **HTML5/CSS3** - Structure et style
- **Tailwind CSS** - Framework CSS moderne
- **Alpine.js** - Interactivité JavaScript
- **Chart.js** - Graphiques et visualisations

### Intégrations
- **Lengo Pay API** - Paiements en ligne
- **ReportLab** - Génération de PDF
- **Pillow** - Traitement d'images
- **python-barcode** - Génération de codes-barres

## 🚀 Installation et Déploiement

### Prérequis
- Python 3.8+
- MySQL 8.0+ (ou SQLite pour développement)
- Redis (optionnel, pour Celery)
- Node.js 14+ (pour les outils de développement)

### Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/stockmanager-pro.git
cd stockmanager-pro

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration de la base de données
python setup_mysql.py

# 5. Créer les plans d'abonnement
python manage.py create_plans

# 6. Démarrer le serveur
python manage.py runserver
```

### Déploiement avec Docker

```bash
# Démarrer tous les services
docker-compose up -d

# L'application sera accessible sur http://localhost:8000
```

## 🔧 Configuration

### Variables d'environnement (.env)
```bash
# Base de données
DB_NAME=stockmanager_db
DB_USER=stockuser
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306

# Lengo Pay
LENGO_PAY_WEBSITE_ID=STOCKMANAGER_PRO
LENGO_PAY_LICENSE_KEY=votre-clé-licence
SITE_URL=http://localhost:8000

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Sécurité
SECRET_KEY=votre-clé-secrète-très-longue
DEBUG=False
```

## 📱 Utilisation

### Premiers Pas
1. **Inscription** - Créez votre compte sur la page d'accueil
2. **Choix du plan** - Sélectionnez l'abonnement adapté à vos besoins
3. **Configuration** - Configurez les informations de votre entreprise
4. **Ajout de produits** - Commencez par ajouter vos catégories et produits
5. **Gestion quotidienne** - Utilisez le tableau de bord pour gérer votre stock

### Comptes de Démonstration
- **Utilisateur** : admin
- **Mot de passe** : admin123

## 📊 API REST

L'application expose une API REST complète (Plan Premium) :

### Endpoints Principaux
```
GET  /inventory/api/v1/products/     # Liste des produits
POST /inventory/api/v1/products/     # Créer un produit
GET  /inventory/api/v1/categories/   # Liste des catégories
GET  /inventory/api/v1/movements/    # Mouvements de stock
GET  /inventory/api/v1/alerts/       # Alertes de stock
```

### Authentification
L'API utilise l'authentification par session Django.

## 🔒 Sécurité et Conformité

- **🔐 Chiffrement SSL/TLS** - Toutes les communications sont sécurisées
- **🛡️ Protection CSRF** - Protection contre les attaques cross-site
- **🔑 Authentification robuste** - Gestion sécurisée des utilisateurs
- **💾 Sauvegardes automatiques** - Vos données sont protégées
- **🇬🇳 Conformité locale** - Respect des réglementations guinéennes

## 📈 Avantages Concurrentiels

### Pour les Petites Entreprises
- **Gratuit pour commencer** - Aucun coût initial
- **Interface simple** - Facile à prendre en main
- **Support en français** - Assistance dans votre langue

### Pour les Entreprises Moyennes
- **Facturation professionnelle** - Documents conformes
- **Multi-utilisateurs** - Travail en équipe
- **Rapports détaillés** - Pilotage de l'activité

### Pour les Grandes Entreprises
- **IA et prédictions** - Optimisation intelligente
- **API complète** - Intégration avec vos systèmes
- **Support 24h/24** - Assistance prioritaire

## 🌍 Spécificités Guinéennes

- **💰 Prix en Francs Guinéens (GNF)** - Devise locale
- **📱 Mobile Money** - Orange Money, MTN Money
- **🏪 Adaptée au commerce local** - Fonctionnalités spécifiques
- **🇫🇷 Interface en français** - Langue officielle
- **📞 Support local** - Équipe basée en Guinée

## 📞 Support et Contact

### Support Technique
- **Plan Gratuit** : Support communautaire WhatsApp
- **Plan Complet** : Support standard par email
- **Plan Premium** : Support prioritaire 24h/24

### Contacts
- **Email** : support@stockmanager-pro.gn
- **WhatsApp** : +224 XXX XXX XXX
- **Site web** : https://stockmanager-pro.gn

## 🎯 Roadmap 2024-2025

### Version 2.0 (Q2 2024)
- [ ] Application mobile native (Android/iOS)
- [ ] Intégration e-commerce (boutique en ligne)
- [ ] Module de comptabilité avancée
- [ ] Gestion des employés et paie

### Version 3.0 (Q4 2024)
- [ ] Multi-entrepôts et multi-magasins
- [ ] Gestion des lots et dates d'expiration
- [ ] Intégration avec les banques locales
- [ ] Marketplace inter-entreprises

### Version 4.0 (2025)
- [ ] IA avancée et machine learning
- [ ] Blockchain pour la traçabilité
- [ ] Intégration IoT (capteurs de stock)
- [ ] Expansion régionale (Afrique de l'Ouest)

## 📄 Licence et Conditions

Ce projet est sous licence propriétaire. L'utilisation est soumise aux conditions d'abonnement.

### Conditions d'Utilisation
- **Plan Gratuit** : Usage personnel et commercial limité
- **Plans Payants** : Usage commercial complet selon les limites du plan
- **Support** : Inclus selon le niveau d'abonnement
- **Mises à jour** : Automatiques et incluses

## 🤝 Partenaires

- **Lengo Pay** - Partenaire paiement officiel
- **Orange Guinée** - Partenaire Mobile Money
- **MTN Guinée** - Partenaire Mobile Money
- **Banques locales** - Partenaires financiers

## 🏆 Témoignages Clients

> *"StockManager Pro a révolutionné la gestion de ma boutique. Je recommande vivement !"*
> **- Fatoumata D., Propriétaire de boutique, Conakry**

> *"L'IA du plan Premium nous aide à prévoir nos commandes. Excellent investissement."*
> **- Mamadou S., Gérant de pharmacie, Kankan**

> *"Interface simple et efficace. Parfait pour débuter dans le commerce."*
> **- Aissatou B., Vendeuse au marché, Labé**

---

**StockManager Pro** - *Gérez votre stock intelligemment !* 🚀

*Développé avec ❤️ en Guinée pour les entreprises africaines*

---

### 📱 Téléchargements et Liens

- **🌐 Site web** : [https://stockmanager-pro.gn](https://stockmanager-pro.gn)
- **📱 App Android** : [Google Play Store](https://play.google.com/store/apps/stockmanager-pro)
- **🍎 App iOS** : [App Store](https://apps.apple.com/app/stockmanager-pro)
- **📚 Documentation** : [https://docs.stockmanager-pro.gn](https://docs.stockmanager-pro.gn)
- **💬 Communauté** : [WhatsApp Community](https://chat.whatsapp.com/stockmanager-pro)

### 🎓 Formation et Ressources

- **📹 Tutoriels vidéo** : [YouTube Channel](https://youtube.com/stockmanager-pro)
- **📖 Guide utilisateur** : [PDF Download](https://stockmanager-pro.gn/guide.pdf)
- **🎯 Webinaires** : Sessions de formation en ligne gratuites
- **👥 Formation sur site** : Disponible pour les plans Premium

---

*Copyright © 2024 StockManager Pro. Tous droits réservés.*