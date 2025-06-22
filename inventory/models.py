from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='subcategories', verbose_name="Catégorie parent")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def full_path(self):
        """Retourne le chemin complet de la catégorie"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Personne de contact")
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro fiscal")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('piece', 'Pièce'),
        ('kg', 'Kilogramme'),
        ('liter', 'Litre'),
        ('meter', 'Mètre'),
        ('box', 'Boîte'),
        ('pack', 'Pack'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    sku = models.CharField(max_length=50, unique=True, verbose_name="Code produit (SKU)")
    barcode = models.CharField(max_length=100, blank=True, unique=True, verbose_name="Code-barres")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Catégorie")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='products', verbose_name="Fournisseur")
    description = models.TextField(blank=True, verbose_name="Description")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece', verbose_name="Unité")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix de revient")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    minimum_stock = models.PositiveIntegerField(default=10, verbose_name="Stock minimum")
    maximum_stock = models.PositiveIntegerField(default=1000, verbose_name="Stock maximum")
    location = models.CharField(max_length=100, blank=True, verbose_name="Emplacement")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Image")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_sku()
        super().save(*args, **kwargs)

    def generate_sku(self):
        """Génère un SKU unique"""
        prefix = self.category.name[:3].upper() if self.category else "PRD"
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    @property
    def stock_status(self):
        if self.is_out_of_stock:
            return "out_of_stock"
        elif self.is_low_stock:
            return "low_stock"
        elif self.quantity >= self.maximum_stock:
            return "overstock"
        return "normal"

    @property
    def stock_value(self):
        return self.quantity * self.price

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrée'),
        ('OUT', 'Sortie'),
        ('ADJUSTMENT', 'Ajustement'),
        ('TRANSFER', 'Transfert'),
        ('RETURN', 'Retour'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements', verbose_name="Produit")
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name="Type de mouvement")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    quantity_before = models.PositiveIntegerField(verbose_name="Quantité avant")
    quantity_after = models.PositiveIntegerField(verbose_name="Quantité après")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    total_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valeur totale")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    date = models.DateTimeField(default=timezone.now, verbose_name="Date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Calculer la valeur totale
        self.total_value = self.quantity * self.unit_price
        
        # Enregistrer les quantités avant/après
        if not self.pk:  # Nouveau mouvement
            self.quantity_before = self.product.quantity
            
            if self.movement_type == 'IN':
                self.quantity_after = self.quantity_before + self.quantity
            elif self.movement_type == 'OUT':
                if self.quantity_before < self.quantity:
                    raise ValidationError("Quantité insuffisante en stock.")
                self.quantity_after = self.quantity_before - self.quantity
            else:  # ADJUSTMENT
                self.quantity_after = self.quantity
        
        super().save(*args, **kwargs)
        
        # Mettre à jour le stock du produit
        if not kwargs.get('skip_stock_update', False):
            Product.objects.filter(pk=self.product.pk).update(
                quantity=self.quantity_after,
                updated_at=timezone.now()
            )

class StockAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Stock faible'),
        ('OUT_OF_STOCK', 'Rupture de stock'),
        ('OVERSTOCK', 'Surstock'),
        ('EXPIRY', 'Expiration proche'),
    ]

    ALERT_STATUS = [
        ('ACTIVE', 'Actif'),
        ('RESOLVED', 'Résolu'),
        ('IGNORED', 'Ignoré'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=ALERT_STATUS, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Alerte de stock"
        verbose_name_plural = "Alertes de stock"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"

class StockReport(models.Model):
    REPORT_TYPES = [
        ('DAILY', 'Journalier'),
        ('WEEKLY', 'Hebdomadaire'),
        ('MONTHLY', 'Mensuel'),
        ('CUSTOM', 'Personnalisé'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES, verbose_name="Type de rapport")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/', null=True, blank=True, verbose_name="Fichier")
    
    class Meta:
        verbose_name = "Rapport de stock"
        verbose_name_plural = "Rapports de stock"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"