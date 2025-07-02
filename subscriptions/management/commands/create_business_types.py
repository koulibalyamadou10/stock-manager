from django.core.management.base import BaseCommand
from subscriptions.models import BusinessType

class Command(BaseCommand):
    help = 'Create default business types'

    def handle(self, *args, **options):
        # Définir les types d'entreprises
        business_types = [
            {
                'type': 'retail',
                'name': 'Commerce de détail / Boutique',
                'description': 'Boutiques, magasins et commerces de détail',
                'icon': 'fas fa-store',
                'has_specific_features': False,
                'specific_features': []
            },
            {
                'type': 'pharmacy',
                'name': 'Pharmacie',
                'description': 'Pharmacies et parapharmacies',
                'icon': 'fas fa-prescription-bottle-alt',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des dates d\'expiration',
                    'Suivi des ordonnances',
                    'Alertes de rupture de stock médicaments',
                    'Gestion des lots et traçabilité'
                ]
            },
            {
                'type': 'restaurant',
                'name': 'Restaurant / Alimentation',
                'description': 'Restaurants, cafés, services de restauration',
                'icon': 'fas fa-utensils',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des ingrédients',
                    'Calcul des coûts de recettes',
                    'Gestion des tables et commandes',
                    'Suivi des dates de péremption'
                ]
            },
            {
                'type': 'electronics',
                'name': 'Électronique',
                'description': 'Magasins d\'électronique et informatique',
                'icon': 'fas fa-laptop',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des numéros de série',
                    'Suivi des garanties',
                    'Gestion des réparations',
                    'Suivi des accessoires'
                ]
            },
            {
                'type': 'fashion',
                'name': 'Mode / Vêtements',
                'description': 'Boutiques de vêtements et accessoires',
                'icon': 'fas fa-tshirt',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des tailles et couleurs',
                    'Suivi des collections',
                    'Gestion des saisons',
                    'Suivi des tendances'
                ]
            },
            {
                'type': 'automotive',
                'name': 'Automobile / Garage',
                'description': 'Garages, concessionnaires, pièces détachées',
                'icon': 'fas fa-car',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des pièces détachées',
                    'Suivi des réparations',
                    'Gestion des rendez-vous',
                    'Historique des véhicules'
                ]
            },
            {
                'type': 'beauty',
                'name': 'Beauté / Salon',
                'description': 'Salons de beauté, coiffure, spa',
                'icon': 'fas fa-cut',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des rendez-vous',
                    'Suivi des clients',
                    'Gestion des services',
                    'Suivi des produits utilisés'
                ]
            },
            {
                'type': 'construction',
                'name': 'Construction / Matériaux',
                'description': 'Entreprises de construction, quincailleries',
                'icon': 'fas fa-hard-hat',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des projets',
                    'Suivi des matériaux',
                    'Gestion des locations d\'équipement',
                    'Calcul des quantités'
                ]
            },
            {
                'type': 'wholesale',
                'name': 'Commerce de gros',
                'description': 'Grossistes et distributeurs',
                'icon': 'fas fa-warehouse',
                'has_specific_features': True,
                'specific_features': [
                    'Gestion des commandes en gros',
                    'Tarification par volume',
                    'Gestion des livraisons',
                    'Suivi des clients professionnels'
                ]
            },
            {
                'type': 'other',
                'name': 'Autre',
                'description': 'Autres types d\'entreprises',
                'icon': 'fas fa-building',
                'has_specific_features': False,
                'specific_features': []
            }
        ]
        
        # Créer les types d'entreprises
        for business_type_data in business_types:
            business_type, created = BusinessType.objects.get_or_create(
                type=business_type_data['type'],
                defaults={
                    'name': business_type_data['name'],
                    'description': business_type_data['description'],
                    'icon': business_type_data['icon'],
                    'has_specific_features': business_type_data['has_specific_features'],
                    'specific_features': business_type_data['specific_features']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Type d'entreprise '{business_type.name}' créé"))
            else:
                self.stdout.write(self.style.WARNING(f"Type d'entreprise '{business_type.name}' existe déjà"))
        
        self.stdout.write(self.style.SUCCESS("Tous les types d'entreprises ont été créés avec succès"))