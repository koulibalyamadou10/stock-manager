#!/usr/bin/env python
"""
Script to set up MySQL database for StockManager Pro
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_database():
    """Set up the database with initial data"""
    
    print("Setting up StockManager Pro database...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_manager.settings')
    django.setup()
    
    try:
        # Run migrations
        print("Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Create superuser
        print("Creating superuser...")
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@stockmanager.com',
                password='admin123'
            )
            print("Superuser 'admin' created with password 'admin123'")
        else:
            print("Superuser 'admin' already exists")
        
        # Create initial data
        print("Creating initial data...")
        create_initial_data()
        
        print("Database setup completed successfully!")
        print("\nYou can now:")
        print("1. Run the server: python manage.py runserver")
        print("2. Access admin: http://localhost:8000/admin/")
        print("3. Login with: admin / admin123")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

def create_initial_data():
    """Create initial categories, suppliers, and sample products"""
    
    from inventory.models import Category, Supplier, Product
    from billing.models import Company, InvoiceTemplate
    
    # Create categories
    categories_data = [
        {'name': 'Électronique', 'description': 'Appareils électroniques et accessoires'},
        {'name': 'Vêtements', 'description': 'Vêtements et accessoires de mode'},
        {'name': 'Alimentation', 'description': 'Produits alimentaires et boissons'},
        {'name': 'Maison & Jardin', 'description': 'Articles pour la maison et le jardin'},
        {'name': 'Santé & Beauté', 'description': 'Produits de santé et cosmétiques'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create suppliers
    suppliers_data = [
        {
            'name': 'TechnoGuinée SARL',
            'email': 'contact@technoguinee.com',
            'phone': '+224 622 123 456',
            'address': 'Kaloum, Conakry, Guinée',
            'contact_person': 'Mamadou Diallo'
        },
        {
            'name': 'Mode Africaine',
            'email': 'info@modeafricaine.gn',
            'phone': '+224 664 789 012',
            'address': 'Madina, Conakry, Guinée',
            'contact_person': 'Fatoumata Camara'
        },
        {
            'name': 'Alimentation Générale',
            'email': 'vente@alimentationgn.com',
            'phone': '+224 655 345 678',
            'address': 'Matam, Conakry, Guinée',
            'contact_person': 'Ibrahima Sow'
        }
    ]
    
    for sup_data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(
            name=sup_data['name'],
            defaults=sup_data
        )
        if created:
            print(f"Created supplier: {supplier.name}")
    
    # Create sample products
    electronics_cat = Category.objects.get(name='Électronique')
    clothing_cat = Category.objects.get(name='Vêtements')
    food_cat = Category.objects.get(name='Alimentation')
    
    techno_supplier = Supplier.objects.get(name='TechnoGuinée SARL')
    mode_supplier = Supplier.objects.get(name='Mode Africaine')
    food_supplier = Supplier.objects.get(name='Alimentation Générale')
    
    products_data = [
        {
            'name': 'Smartphone Samsung Galaxy A54',
            'category': electronics_cat,
            'supplier': techno_supplier,
            'description': 'Smartphone Android avec écran 6.4 pouces',
            'price': 2500000,  # 2,500,000 GNF
            'cost_price': 2000000,
            'quantity': 25,
            'minimum_stock': 5,
            'maximum_stock': 100,
            'unit': 'piece'
        },
        {
            'name': 'Boubou Traditionnel Homme',
            'category': clothing_cat,
            'supplier': mode_supplier,
            'description': 'Boubou traditionnel guinéen en coton',
            'price': 350000,  # 350,000 GNF
            'cost_price': 250000,
            'quantity': 15,
            'minimum_stock': 3,
            'maximum_stock': 50,
            'unit': 'piece'
        },
        {
            'name': 'Riz Local 25kg',
            'category': food_cat,
            'supplier': food_supplier,
            'description': 'Riz local de qualité supérieure',
            'price': 450000,  # 450,000 GNF
            'cost_price': 350000,
            'quantity': 50,
            'minimum_stock': 10,
            'maximum_stock': 200,
            'unit': 'kg'
        }
    ]
    
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults=prod_data
        )
        if created:
            print(f"Created product: {product.name}")
    
    # Create company information
    company_data = {
        'name': 'Mon Entreprise SARL',
        'address': 'Kaloum, Conakry, République de Guinée',
        'phone': '+224 622 000 000',
        'email': 'contact@monentreprise.gn',
        'tax_number': 'NIF123456789',
        'bank_details': 'Banque Centrale de Guinée\nCompte: 123456789\nIBAN: GN123456789'
    }
    
    company, created = Company.objects.get_or_create(
        name=company_data['name'],
        defaults=company_data
    )
    if created:
        print(f"Created company: {company.name}")
    
    # Create default invoice template
    template_data = {
        'name': 'Modèle Standard',
        'is_default': True,
        'header_color': '#3b82f6',
        'font_family': 'Arial',
        'show_logo': True,
        'footer_text': 'Merci pour votre confiance !',
        'terms_conditions': 'Paiement à 30 jours. Retard de paiement entraîne des pénalités.'
    }
    
    template, created = InvoiceTemplate.objects.get_or_create(
        name=template_data['name'],
        defaults=template_data
    )
    if created:
        print(f"Created invoice template: {template.name}")

if __name__ == '__main__':
    setup_database()