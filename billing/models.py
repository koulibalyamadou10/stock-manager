from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from datetime import datetime

class Company(models.Model):
    """Informations de l'entreprise pour la facturation"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Site web")
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro fiscal")
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name="Logo")
    bank_details = models.TextField(blank=True, verbose_name="Coordonnées bancaires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"

    def __str__(self):
        return self.name

class Customer(models.Model):
    """Modèle pour les clients"""
    CUSTOMER_TYPES = [
        ('individual', 'Particulier'),
        ('company', 'Entreprise'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom/Raison sociale")
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='individual', verbose_name="Type de client")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro fiscal")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['name']

    def __str__(self):
        return self.name

class InvoiceTemplate(models.Model):
    """Modèles de factures personnalisables"""
    name = models.CharField(max_length=100, verbose_name="Nom du modèle")
    is_default = models.BooleanField(default=False, verbose_name="Modèle par défaut")
    header_color = models.CharField(max_length=7, default='#3b82f6', verbose_name="Couleur d'en-tête")
    font_family = models.CharField(max_length=50, default='Arial', verbose_name="Police")
    show_logo = models.BooleanField(default=True, verbose_name="Afficher le logo")
    footer_text = models.TextField(blank=True, verbose_name="Texte de pied de page")
    terms_conditions = models.TextField(blank=True, verbose_name="Conditions générales")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modèle de facture"
        verbose_name_plural = "Modèles de factures"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default template
            InvoiceTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class Invoice(models.Model):
    """Modèle principal pour les factures"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]

    PAYMENT_TERMS = [
        (0, 'Paiement immédiat'),
        (15, '15 jours'),
        (30, '30 jours'),
        (45, '45 jours'),
        (60, '60 jours'),
    ]

    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    
    # Relations
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices', verbose_name="Client")
    template = models.ForeignKey(InvoiceTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Modèle")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    # Dates
    issue_date = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    due_date = models.DateField(verbose_name="Date d'échéance")
    
    # Statut et conditions
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    payment_terms = models.IntegerField(choices=PAYMENT_TERMS, default=30, verbose_name="Conditions de paiement")
    
    # Montants
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Sous-total")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux de TVA (%)")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant TVA")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant remise")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant total")
    
    # Notes et références
    notes = models.TextField(blank=True, verbose_name="Notes")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyée le")
    
    # Fichier PDF généré
    pdf_file = models.FileField(upload_to='invoices/pdf/', blank=True, null=True, verbose_name="Fichier PDF")

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-created_at']

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calculate due date based on payment terms
        if not self.due_date:
            from datetime import timedelta
            self.due_date = self.issue_date + timedelta(days=self.payment_terms)
        
        # Calculate totals
        self.calculate_totals()
        
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        """Génère un numéro de facture automatique"""
        year = timezone.now().year
        month = timezone.now().month
        
        # Format: YYYY-MM-XXXX
        prefix = f"{year}-{month:02d}-"
        
        # Get the last invoice number for this month
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"

    def calculate_totals(self):
        """Calcule les totaux de la facture"""
        # Calculate subtotal from invoice items
        self.subtotal = sum(item.total for item in self.items.all())
        
        # Calculate discount
        if self.discount_rate > 0:
            self.discount_amount = (self.subtotal * self.discount_rate) / 100
        else:
            self.discount_amount = 0
        
        # Calculate tax
        taxable_amount = self.subtotal - self.discount_amount
        if self.tax_rate > 0:
            self.tax_amount = (taxable_amount * self.tax_rate) / 100
        else:
            self.tax_amount = 0
        
        # Calculate total
        self.total_amount = taxable_amount + self.tax_amount

    @property
    def is_overdue(self):
        """Vérifie si la facture est en retard"""
        return self.status in ['sent'] and self.due_date < timezone.now().date()

    @property
    def days_until_due(self):
        """Nombre de jours jusqu'à l'échéance"""
        return (self.due_date - timezone.now().date()).days

    def mark_as_sent(self):
        """Marque la facture comme envoyée"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()

    def mark_as_paid(self):
        """Marque la facture comme payée"""
        self.status = 'paid'
        self.save()

class InvoiceItem(models.Model):
    """Lignes de facture"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name="Facture")
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Produit")
    description = models.CharField(max_length=200, verbose_name="Description")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Prix unitaire")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update invoice totals
        if self.invoice_id:
            self.invoice.calculate_totals()
            self.invoice.save()

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"

class Payment(models.Model):
    """Suivi des paiements"""
    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
        ('bank_transfer', 'Virement bancaire'),
        ('card', 'Carte bancaire'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Autre'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name="Facture")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name="Montant")
    payment_date = models.DateField(default=timezone.now, verbose_name="Date de paiement")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Méthode de paiement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Enregistré par")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Paiement {self.amount} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Check if invoice is fully paid
        total_payments = self.invoice.payments.aggregate(
            total=models.Sum('amount'))['total'] or 0
        
        if total_payments >= self.invoice.total_amount:
            self.invoice.mark_as_paid()

class EmailLog(models.Model):
    """Journal des emails envoyés"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='email_logs', verbose_name="Facture")
    recipient = models.EmailField(verbose_name="Destinataire")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Envoyé le")
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Envoyé par")
    success = models.BooleanField(default=True, verbose_name="Succès")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")

    class Meta:
        verbose_name = "Journal d'email"
        verbose_name_plural = "Journaux d'emails"
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email {self.invoice.invoice_number} à {self.recipient}"