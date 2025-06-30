# StockManager Pro - Système de Gestion de Stock Intelligent

## 📋 Description

StockManager Pro est une application web complète de gestion de stock et de facturation développée avec Django. Elle offre une solution moderne et intelligente pour gérer votre inventaire, créer des factures professionnelles et analyser vos performances commerciales.

## ✨ Fonctionnalités Principales

### 🏪 Gestion de Stock Intelligente
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

### 🤖 Intelligence Artificielle
- ✅ Prédictions de ventes basées sur l'historique
- ✅ Recommandations de réapprovisionnement
- ✅ Détection automatique des tendances de vente
- ✅ Optimisation des niveaux de stock minimum
- ✅ Analyse prédictive des meilleures périodes
- ✅ Assistant intelligent pour la prise de décision

## 🛠️ Prérequis

### Système
- Python 3.8 ou supérieur
- Node.js 14+ (pour les outils de développement front-end)
- Git

### Base de Données (au choix)
- **SQLite** (par défaut, pour développement)
- **MySQL 8.0+** (recommandé pour production)
- **PostgreSQL 12+** (alternative)

### Services Optionnels
- **Redis** (pour le cache et Celery)
- **Docker & Docker Compose** (pour déploiement conteneurisé)

## 🚀 Installation

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/stockmanager-pro.git
cd stockmanager-pro
```

### 2. Créer un Environnement Virtuel
```bash
python -m venv venv

# Sur Windows
venv\Scripts\activate

# Sur Linux/Mac
source venv/bin/activate
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la Base de Données

#### Option A: SQLite (Développement)
```bash
# Aucune configuration supplémentaire nécessaire
python manage.py migrate
```

#### Option B: MySQL (Production)
```bash
# 1. Créer la base de données MySQL
mysql -u root -p
CREATE DATABASE stockmanager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'stockuser'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON stockmanager_db.* TO 'stockuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres MySQL

# 3. Installer le client MySQL
pip install mysqlclient

# 4. Exécuter les migrations
python manage.py migrate
```

### 5. Créer les Données Initiales
```bash
# Exécuter le script de configuration
python setup_mysql.py
```

### 6. Créer un Superutilisateur (si pas fait automatiquement)
```bash
python manage.py createsuperuser
```

### 7. Collecter les Fichiers Statiques
```bash
python manage.py collectstatic
```

## 🏃‍♂️ Démarrage

### Développement
```bash
# Démarrer le serveur de développement
python manage.py runserver

# L'application sera accessible sur http://localhost:8000
```

### Production avec Docker
```bash
# Construire et démarrer tous les services
docker-compose up -d

# L'application sera accessible sur http://localhost:8000
```

## 📱 Utilisation

### Accès à l'Application
- **Interface principale**: http://localhost:8000
- **Administration**: http://localhost:8000/admin/
- **API REST**: http://localhost:8000/inventory/api/v1/

### Comptes par Défaut
- **Utilisateur**: admin
- **Mot de passe**: admin123

### Premiers Pas
1. Connectez-vous avec le compte admin
2. Configurez les informations de votre entreprise
3. Créez vos catégories de produits
4. Ajoutez vos fournisseurs
5. Enregistrez vos premiers produits
6. Commencez à gérer votre stock !

## 🔧 Configuration Avancée

### Variables d'Environnement (.env)
```bash
# Base de données
DB_NAME=stockmanager_db
DB_USER=stockuser
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306

# Sécurité
SECRET_KEY=votre-clé-secrète-très-longue
DEBUG=False

# Email (pour envoi de factures)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0
```

### Tâches Automatisées (Celery)
```bash
# Démarrer le worker Celery
celery -A celery_app worker --loglevel=info

# Démarrer le scheduler Celery Beat
celery -A celery_app beat --loglevel=info
```

### Commandes de Gestion Disponibles
```bash
# Générer des codes-barres pour tous les produits
python manage.py generate_barcodes

# Envoyer les alertes de stock
python manage.py stock_alerts

# Créer une sauvegarde de la base de données
python manage.py backup_database

# Mettre à jour les points de réapprovisionnement
python manage.py shell -c "from inventory.tasks import update_reorder_points; update_reorder_points()"
```

## 📊 API REST

L'application expose une API REST complète pour l'intégration avec d'autres systèmes.

### Endpoints Principaux
- `GET /inventory/api/v1/products/` - Liste des produits
- `POST /inventory/api/v1/products/` - Créer un produit
- `GET /inventory/api/v1/categories/` - Liste des catégories
- `GET /inventory/api/v1/movements/` - Mouvements de stock
- `GET /inventory/api/v1/alerts/` - Alertes de stock
- `GET /inventory/api/v1/analytics/dashboard_stats/` - Statistiques du tableau de bord

### Authentification
L'API utilise l'authentification par session Django. Connectez-vous via l'interface web pour accéder à l'API.

## 🔒 Sécurité

### Recommandations de Production
- Changez la `SECRET_KEY` par défaut
- Définissez `DEBUG=False`
- Configurez `ALLOWED_HOSTS` avec vos domaines
- Utilisez HTTPS en production
- Configurez un serveur web (Nginx/Apache) devant Django
- Utilisez un serveur WSGI (Gunicorn/uWSGI)

### Sauvegarde
```bash
# Sauvegarde automatique quotidienne
python manage.py backup_database

# Sauvegarde manuelle
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

## 🐛 Dépannage

### Problèmes Courants

#### Erreur de Base de Données
```bash
# Réinitialiser les migrations
python manage.py migrate --fake-initial
```

#### Problèmes de Permissions
```bash
# Sur Linux/Mac, donner les permissions aux fichiers media
chmod -R 755 media/
```

#### Erreurs de Dépendances
```bash
# Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt
```

## 📈 Performance

### Optimisations Recommandées
- Utilisez Redis pour le cache en production
- Configurez un CDN pour les fichiers statiques
- Optimisez les requêtes de base de données
- Utilisez un serveur de base de données dédié

### Monitoring
- Logs disponibles dans `/logs/`
- Métriques de performance via l'API analytics
- Alertes automatiques par email

## 🤝 Contribution

### Développement
```bash
# Installer les dépendances de développement
pip install -r requirements-dev.txt

# Exécuter les tests
python manage.py test

# Vérifier le style de code
flake8 .
black .
```

### Structure du Projet
```
stockmanager-pro/
├── inventory/          # App principale de gestion de stock
├── billing/           # App de facturation
├── static/           # Fichiers statiques
├── media/            # Fichiers uploadés
├── templates/        # Templates HTML
├── requirements.txt  # Dépendances Python
├── docker-compose.yml # Configuration Docker
└── manage.py        # Script de gestion Django
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- **Documentation**: [Wiki du projet](https://github.com/votre-username/stockmanager-pro/wiki)
- **Issues**: [GitHub Issues](https://github.com/votre-username/stockmanager-pro/issues)
- **Email**: support@stockmanager-pro.com

## 🎯 Roadmap

### Version 2.0 (À venir)
- [ ] Application mobile (React Native)
- [ ] Intégration e-commerce
- [ ] Multi-entrepôts
- [ ] Gestion des lots et dates d'expiration
- [ ] Rapports avancés avec BI
- [ ] API GraphQL

---

**StockManager Pro** - Gérez votre stock intelligemment ! 🚀