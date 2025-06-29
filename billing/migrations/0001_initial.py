# Generated by Django 5.2.2 on 2025-01-XX XX:XX

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name="Nom de l'entreprise")),
                ('address', models.TextField(verbose_name='Adresse')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('website', models.URLField(blank=True, verbose_name='Site web')),
                ('tax_number', models.CharField(blank=True, max_length=50, verbose_name='Numéro fiscal')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company/', verbose_name='Logo')),
                ('bank_details', models.TextField(blank=True, verbose_name='Coordonnées bancaires')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Entreprise',
                'verbose_name_plural': 'Entreprises',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nom/Raison sociale')),
                ('customer_type', models.CharField(choices=[('individual', 'Particulier'), ('company', 'Entreprise')], default='individual', max_length=20, verbose_name='Type de client')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('address', models.TextField(blank=True, verbose_name='Adresse')),
                ('tax_number', models.CharField(blank=True, max_length=50, verbose_name='Numéro fiscal')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom du modèle')),
                ('is_default', models.BooleanField(default=False, verbose_name='Modèle par défaut')),
                ('header_color', models.CharField(default='#3b82f6', max_length=7, verbose_name="Couleur d'en-tête")),
                ('font_family', models.CharField(default='Arial', max_length=50, verbose_name='Police')),
                ('show_logo', models.BooleanField(default=True, verbose_name='Afficher le logo')),
                ('footer_text', models.TextField(blank=True, verbose_name='Texte de pied de page')),
                ('terms_conditions', models.TextField(blank=True, verbose_name='Conditions générales')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Modèle de facture',
                'verbose_name_plural': 'Modèles de factures',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('invoice_number', models.CharField(max_length=50, unique=True, verbose_name='Numéro de facture')),
                ('issue_date', models.DateField(default=django.utils.timezone.now, verbose_name="Date d'émission")),
                ('due_date', models.DateField(verbose_name="Date d'échéance")),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('sent', 'Envoyée'), ('paid', 'Payée'), ('overdue', 'En retard'), ('cancelled', 'Annulée')], default='draft', max_length=20, verbose_name='Statut')),
                ('payment_terms', models.IntegerField(choices=[(0, 'Paiement immédiat'), (15, '15 jours'), (30, '30 jours'), (45, '45 jours'), (60, '60 jours')], default=30, verbose_name='Conditions de paiement')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Sous-total')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Taux de TVA (%)')),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Montant TVA')),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Remise (%)')),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Montant remise')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Montant total')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('reference', models.CharField(blank=True, max_length=100, verbose_name='Référence')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='Envoyée le')),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='invoices/pdf/', verbose_name='Fichier PDF')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='billing.customer', verbose_name='Client')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='billing.invoicetemplate', verbose_name='Modèle')),
            ],
            options={
                'verbose_name': 'Facture',
                'verbose_name_plural': 'Factures',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200, verbose_name='Description')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Quantité')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Prix unitaire')),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Total')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Ordre')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='billing.invoice', verbose_name='Facture')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.product', verbose_name='Produit')),
            ],
            options={
                'verbose_name': 'Ligne de facture',
                'verbose_name_plural': 'Lignes de facture',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Montant')),
                ('payment_date', models.DateField(default=django.utils.timezone.now, verbose_name='Date de paiement')),
                ('payment_method', models.CharField(choices=[('cash', 'Espèces'), ('check', 'Chèque'), ('bank_transfer', 'Virement bancaire'), ('card', 'Carte bancaire'), ('mobile_money', 'Mobile Money'), ('other', 'Autre')], max_length=20, verbose_name='Méthode de paiement')),
                ('reference', models.CharField(blank=True, max_length=100, verbose_name='Référence')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Enregistré par')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='billing.invoice', verbose_name='Facture')),
            ],
            options={
                'verbose_name': 'Paiement',
                'verbose_name_plural': 'Paiements',
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.EmailField(max_length=254, verbose_name='Destinataire')),
                ('subject', models.CharField(max_length=200, verbose_name='Sujet')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Envoyé le')),
                ('success', models.BooleanField(default=True, verbose_name='Succès')),
                ('error_message', models.TextField(blank=True, verbose_name="Message d'erreur")),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to='billing.invoice', verbose_name='Facture')),
                ('sent_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Envoyé par')),
            ],
            options={
                'verbose_name': "Journal d'email",
                'verbose_name_plural': "Journaux d'emails",
                'ordering': ['-sent_at'],
            },
        ),
    ]