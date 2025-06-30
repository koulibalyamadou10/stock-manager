from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

class Plan(models.Model):
    PLAN_TYPES = [
        ('free', 'Gratuit'),
        ('complete', 'Complet'),
        ('premium', 'Premium'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom du plan")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True, verbose_name="Type de plan")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (GNF)")
    description = models.TextField(verbose_name="Description")
    features = models.JSONField(default=list, verbose_name="Fonctionnalités")
    max_products = models.IntegerField(null=True, blank=True, verbose_name="Nombre max de produits")
    max_users = models.IntegerField(null=True, blank=True, verbose_name="Nombre max d'utilisateurs")
    max_invoices_per_month = models.IntegerField(null=True, blank=True, verbose_name="Factures max par mois")
    has_ai_features = models.BooleanField(default=False, verbose_name="Fonctionnalités IA")
    has_advanced_reports = models.BooleanField(default=False, verbose_name="Rapports avancés")
    has_api_access = models.BooleanField(default=False, verbose_name="Accès API")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Plan d'abonnement"
        verbose_name_plural = "Plans d'abonnement"
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.price} GNF"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
        ('pending', 'En attente'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, verbose_name="Plan")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    auto_renew = models.BooleanField(default=True, verbose_name="Renouvellement automatique")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()
    
    @property
    def days_remaining(self):
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    def extend_subscription(self, months=1):
        """Étendre l'abonnement"""
        if self.is_active:
            self.end_date += timedelta(days=30 * months)
        else:
            self.start_date = timezone.now()
            self.end_date = timezone.now() + timedelta(days=30 * months)
            self.status = 'active'
        self.save()

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    PAYMENT_METHODS = [
        ('lengo_pay', 'Lengo Pay'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    currency = models.CharField(max_length=3, default='GNF', verbose_name="Devise")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Méthode de paiement")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name="Statut")
    
    # Lengo Pay specific fields
    lengo_payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Paiement Lengo")
    lengo_payment_url = models.URLField(blank=True, null=True, verbose_name="URL Paiement Lengo")
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Transaction")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    failure_reason = models.TextField(blank=True, null=True, verbose_name="Raison de l'échec")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Paiement {self.amount} GNF - {self.status}"

class UsageLimit(models.Model):
    """Suivi des limites d'utilisation par abonnement"""
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE, related_name='usage')
    products_count = models.IntegerField(default=0, verbose_name="Nombre de produits")
    invoices_this_month = models.IntegerField(default=0, verbose_name="Factures ce mois")
    users_count = models.IntegerField(default=1, verbose_name="Nombre d'utilisateurs")
    api_calls_this_month = models.IntegerField(default=0, verbose_name="Appels API ce mois")
    last_reset_date = models.DateTimeField(default=timezone.now, verbose_name="Dernière réinitialisation")
    
    class Meta:
        verbose_name = "Limite d'utilisation"
        verbose_name_plural = "Limites d'utilisation"
    
    def reset_monthly_counters(self):
        """Réinitialiser les compteurs mensuels"""
        self.invoices_this_month = 0
        self.api_calls_this_month = 0
        self.last_reset_date = timezone.now()
        self.save()
    
    def can_create_product(self):
        """Vérifier si l'utilisateur peut créer un produit"""
        if self.subscription.plan.max_products is None:
            return True
        return self.products_count < self.subscription.plan.max_products
    
    def can_create_invoice(self):
        """Vérifier si l'utilisateur peut créer une facture"""
        if self.subscription.plan.max_invoices_per_month is None:
            return True
        return self.invoices_this_month < self.subscription.plan.max_invoices_per_month
    
    def can_add_user(self):
        """Vérifier si l'utilisateur peut ajouter un utilisateur"""
        if self.subscription.plan.max_users is None:
            return True
        return self.users_count < self.subscription.plan.max_users