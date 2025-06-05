from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import json
import csv
import xlsxwriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .models import Category, Product, StockMovement, Supplier, StockReport
from .forms import CategoryForm, ProductForm, StockMovementForm, SupplierForm, ReportForm

@login_required
def dashboard(request):
    """Dashboard view with key statistics and charts."""
    # Get counts
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.count()
    
    # Get low stock products
    low_stock_products = Product.objects.filter(quantity__lte=F('minimum_stock'))
    
    # Get recent movements
    recent_movements = StockMovement.objects.select_related('product').order_by('-date')[:10]
    
    # Get stock value
    total_stock_value = Product.objects.aggregate(
        value=Sum(F('quantity') * F('price')))['value'] or 0
    
    # Get movement statistics for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    movements_30_days = StockMovement.objects.filter(date__gte=thirty_days_ago)
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock_products': low_stock_products,
        'recent_movements': recent_movements,
        'total_stock_value': total_stock_value,
    }
    return render(request, 'inventory/dashboard.html', context)

# Category Views
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie ajoutée avec succès.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Catégorie modifiée avec succès.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Catégorie supprimée avec succès.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/category_confirm_delete.html', {'category': category})

# Product Views
@login_required
def product_list(request):
    products = Product.objects.select_related('category', 'supplier').all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit ajouté avec succès.')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit modifié avec succès.')
            return redirect('inventory:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produit supprimé avec succès.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

# Stock Movement Views
@login_required
def stock_entry(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'IN'
            movement.save()
            messages.success(request, 'Entrée de stock enregistrée avec succès.')
            return redirect('inventory:stock_history')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/stock_movement_form.html', {
        'form': form,
        'title': 'Nouvelle entrée de stock'
    })

@login_required
def stock_exit(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'OUT'
            if movement.quantity > movement.product.quantity:
                messages.error(request, 'Quantité insuffisante en stock.')
                return render(request, 'inventory/stock_movement_form.html', {
                    'form': form,
                    'title': 'Nouvelle sortie de stock'
                })
            movement.save()
            messages.success(request, 'Sortie de stock enregistrée avec succès.')
            return redirect('inventory:stock_history')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/stock_movement_form.html', {
        'form': form,
        'title': 'Nouvelle sortie de stock'
    })

# Supplier Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur ajouté avec succès.')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {'form': form})

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur modifié avec succès.')
            return redirect('inventory:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form.html', {'form': form})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Fournisseur supprimé avec succès.')
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/supplier_confirm_delete.html', {'supplier': supplier})

@login_required
def stock_history(request):
    # Get filter parameters
    product_id = request.GET.get('product')
    movement_type = request.GET.get('movement_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset
    movements = StockMovement.objects.select_related('product').order_by('-date')

    # Apply filters
    if product_id:
        movements = movements.filter(product_id=product_id)
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    if start_date:
        movements = movements.filter(date__gte=start_date)
    if end_date:
        movements = movements.filter(date__lte=end_date)

    # Calculate statistics
    total_movements = movements.count()
    total_entries = movements.filter(movement_type='IN').count()
    total_exits = movements.filter(movement_type='OUT').count()
    total_value = movements.aggregate(
        value=Sum(F('quantity') * F('unit_price')))['value'] or 0

    # Get all products for the filter dropdown
    products = Product.objects.all()

    context = {
        'movements': movements,
        'products': products,
        'total_movements': total_movements,
        'total_entries': total_entries,
        'total_exits': total_exits,
        'total_value': total_value,
        'query_params': request.GET.urlencode()
    }
    return render(request, 'inventory/stock_history.html', context)

# Statistics and Charts
@login_required
def stock_movement_chart(request):
    """API endpoint for stock movement chart data."""
    labels = []
    entries_data = []
    exits_data = []
    
    # Get data for the last 30 days
    for i in range(30, -1, -1):
        date = timezone.now() - timedelta(days=i)
        labels.append(date.strftime('%Y-%m-%d'))
        
        entries = StockMovement.objects.filter(
            movement_type='IN',
            date__date=date.date()
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        exits = StockMovement.objects.filter(
            movement_type='OUT',
            date__date=date.date()
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        entries_data.append(entries)
        exits_data.append(exits)
    
    return JsonResponse({
        'labels': labels,
        'entries': entries_data,
        'exits': exits_data,
    })

@login_required
def product_category_chart(request):
    """API endpoint for product distribution by category chart data."""
    categories = Category.objects.annotate(product_count=Count('products'))
    
    return JsonResponse({
        'labels': [cat.name for cat in categories],
        'data': [cat.product_count for cat in categories],
    })

@login_required
def low_stock_products(request):
    """API endpoint for low stock products data."""
    products = Product.objects.filter(quantity__lte=F('minimum_stock'))
    data = [{
        'name': p.name,
        'quantity': p.quantity,
        'minimum': p.minimum_stock,
    } for p in products]
    return JsonResponse({'products': data})

# Export functionality
@login_required
def export_products(request):
    """Export products list to Excel."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Write headers
    headers = ['Nom', 'Catégorie', 'Prix', 'Quantité', 'Stock minimum']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Write data
    products = Product.objects.select_related('category').all()
    for row, product in enumerate(products, 1):
        worksheet.write(row, 0, product.name)
        worksheet.write(row, 1, product.category.name)
        worksheet.write(row, 2, float(product.price))
        worksheet.write(row, 3, product.quantity)
        worksheet.write(row, 4, product.minimum_stock)

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=products.xlsx'
    return response

@login_required
def export_movements(request):
    """Export stock movements to PDF."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=stock_movements.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Get data
    movements = StockMovement.objects.select_related('product').order_by('-date')[:50]
    data = [['Date', 'Produit', 'Type', 'Quantité', 'Prix unitaire']]
    for movement in movements:
        data.append([
            movement.date.strftime('%Y-%m-%d %H:%M'),
            movement.product.name,
            movement.get_movement_type_display(),
            str(movement.quantity),
            str(movement.unit_price)
        ])

    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    doc.build(elements)
    return response

@login_required
def statistics(request):
    """Statistics view with detailed analytics."""
    # Get date range
    period = request.GET.get('period', '30')
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))

    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d')
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d')

    # Calculate statistics
    total_stock_value = Product.objects.aggregate(
        value=Sum(F('quantity') * F('price')))['value'] or 0

    # Previous period for comparison
    period_length = (end_date - start_date).days
    prev_end_date = start_date
    prev_start_date = prev_end_date - timedelta(days=period_length)
    
    prev_stock_value = StockMovement.objects.filter(
        date__range=[prev_start_date, prev_end_date]
    ).aggregate(
        value=Sum(F('quantity') * F('unit_price'))
    )['value'] or 0

    if prev_stock_value > 0:
        stock_value_change = ((total_stock_value - prev_stock_value) / prev_stock_value) * 100
    else:
        stock_value_change = 0

    # Movement statistics
    movements = StockMovement.objects.filter(date__range=[start_date, end_date])
    total_entries = movements.filter(movement_type='IN').count()
    total_exits = movements.filter(movement_type='OUT').count()
    total_entries_value = movements.filter(movement_type='IN').aggregate(
        value=Sum(F('quantity') * F('unit_price')))['value'] or 0
    total_exits_value = movements.filter(movement_type='OUT').aggregate(
        value=Sum(F('quantity') * F('unit_price')))['value'] or 0

    # Low stock products
    low_stock_products = Product.objects.filter(quantity__lte=F('minimum_stock'))
    low_stock_count = low_stock_products.count()
    total_products = Product.objects.count()

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_stock_value': total_stock_value,
        'stock_value_change': stock_value_change,
        'total_entries': total_entries,
        'total_exits': total_exits,
        'total_entries_value': total_entries_value,
        'total_exits_value': total_exits_value,
        'low_stock_count': low_stock_count,
        'total_products': total_products,
        'low_stock_products': low_stock_products
    }
    return render(request, 'inventory/statistics.html', context)
