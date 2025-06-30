from django.core.management.base import BaseCommand
from subscriptions.models import Plan

class Command(BaseCommand):
    help = 'Create default subscription plans'

    def handle(self, *args, **options):
        # Plan Gratuit
        free_plan, created = Plan.objects.get_or_create(
            plan_type='free',
            defaults={
                'name': 'Gratuit',
                'price': 0,
                'description': 'Idéal pour les petits vendeurs ou commerçants débutants',
                'features': [
                    'Gestion simple du stock (ajout, sortie, alerte)',
                    'Enregistrement des ventes quotidiennes',
                    'Historique des opérations',
                    'Alertes de stock minimum',
                    'Interface mobile responsive',
                    'Support communautaire par WhatsApp',
                    '1 seul utilisateur',
                    '1 seule boutique'
                ],
                'max_products': 100,
                'max_users': 1,
                'max_invoices_per_month': 10,
                'has_ai_features': False,
                'has_advanced_reports': False,
                'has_api_access': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Plan {free_plan.name} créé'))

        # Plan Complet
        complete_plan, created = Plan.objects.get_or_create(
            plan_type='complete',
            defaults={
                'name': 'Complet',
                'price': 80000,
                'description': 'Pour les commerces structurés : boutiques, librairies, points de vente',
                'features': [
                    'Toutes les fonctionnalités Start +',
                    'Multi-utilisateur (jusqu\'à 3)',
                    'Statistiques simplifiées (ventes, produits, charges)',
                    'Gestion des flux financiers (entrées/sorties, bénéfices)',
                    'Génération de factures PDF',
                    'Envoi d\'email automatique au client',
                    'Sauvegarde cloud et sécurité renforcée',
                    'Support standard'
                ],
                'max_products': 1000,
                'max_users': 3,
                'max_invoices_per_month': 100,
                'has_ai_features': False,
                'has_advanced_reports': True,
                'has_api_access': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Plan {complete_plan.name} créé'))

        # Plan Premium
        premium_plan, created = Plan.objects.get_or_create(
            plan_type='premium',
            defaults={
                'name': 'Premium',
                'price': 200000,
                'description': 'Pour les gestionnaires, franchises, pharmacies, salons, garagistes',
                'features': [
                    'Toutes les fonctionnalités Business +',
                    'Nombre illimité de boutiques',
                    'Gestion multi-utilisateurs illimitée',
                    'Gestion avancée du stock (FIFO, historiques)',
                    'Comptabilité simplifiée (charges, rentabilité)',
                    'Modules personnalisés selon activité',
                    'Exports CSV, sauvegarde automatique',
                    'Accès à l\'IA (assistant + prévision ventes)',
                    'Support prioritaire 24h/24'
                ],
                'max_products': None,  # Illimité
                'max_users': None,     # Illimité
                'max_invoices_per_month': None,  # Illimité
                'has_ai_features': True,
                'has_advanced_reports': True,
                'has_api_access': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Plan {premium_plan.name} créé'))

        self.stdout.write(self.style.SUCCESS('Tous les plans ont été créés avec succès'))