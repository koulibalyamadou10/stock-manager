from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q, Avg
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from datetime import datetime, timedelta
import json
import csv
import xlsxwriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .models import Category, Product, StockMovement, Supplier, StockReport, StockAlert
from .forms import CategoryForm, ProductForm, StockMovementForm, SupplierForm, ReportForm

@login_required
def dashboard(request):
    """Dashboard view with real-time statistics and charts."""
    # Get counts
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Get low stock products
    low_stock_products = Product.objects.filter(
        quantity__lte=F('minimum_stock'),
        is_active=True
    )
    
    # Get recent movements (last 24 hours)
    yesterday = timezone.now() - timedelta(days=1)
    recent_movements = StockMovement.objects.filter(
        date__gte=yesterday
    ).select_related('product').order_by('-date')[:10]
    
    recent_movements_count = StockMovement.objects.filter(date__gte=yesterday).count()
    
    # Get stock value
    total_stock_value = Product.objects.filter(is_active=True).aggregate(
        value=Sum(F('quantity') * F('price')))['value'] or 0
    
    # Create alerts for low stock products
    for product in low_stock_products:
        StockAlert.objects.get_or_create(
            product=product,
            alert_type='LOW_STOCK' if product.quantity > 0 else 'OUT_OF_STOCK',
            status='ACTIVE',
            defaults={
                'message': f"Stock faible pour {product.name}: {product.quantity}/{product.minimum_stock}"
            }
        )
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock_products': low_stock_products,
        'recent_movements': recent_movements,
        'recent_movements_count': recent_movements_count,
        'total_stock_value': total_stock_value,
    }
    return render(request, 'inventory/dashboard.html', context)

# API Endpoints for real-time data
@login_required
def api_alerts(request):
    """API endpoint for active alerts."""
    alerts = StockAlert.objects.filter(status='ACTIVE').select_related('product')
    data = [{
        'id': alert.id,
        'type': alert.alert_type,
        'product_name': alert.product.name,
        'message': alert.message,
        'created_at': alert.created_at.isoformat()
    } for alert in alerts]
    return JsonResponse(data, safe=False)

@login_required
def api_recent_movements(request):
    """API endpoint for recent stock movements."""
    movements = StockMovement.objects.select_related('product').order_by('-date')[:10]
    data = [{
        'id': str(movement.id),
        'product_name': movement.product.name,
        'movement_type': movement.movement_type,
        'movement_type_display': movement.get_movement_type_display(),
        'quantity': movement.quantity,
        'total_value': float(movement.total_value),
        'date': movement.date.isoformat()
    } for movement in movements]
    return JsonResponse(data, safe=False)

@login_required
def api_alerts_count(request):
    """API endpoint for alerts count."""
    count = StockAlert.objects.filter(status='ACTIVE').count()
    return JsonResponse({'count': count})

@login_required
def api_search_products(request):
    """API endpoint for product search."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query) | Q(barcode__icontains=query),
        is_active=True
    )[:10]
    
    data = [{
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'barcode': product.barcode,
        'quantity': product.quantity,
        'price': float(product.price)
    } for product in products]
    
    return JsonResponse({'results': data})

@login_required
def api_search_by_barcode(request):
    """API endpoint for barcode search."""
    code = request.GET.get('code', '')
    if not code:
        return JsonResponse({'found': False})
    
    try:
        product = Product.objects.get(barcode=code, is_active=True)
        return JsonResponse({
            'found': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'quantity': product.quantity,
                'price': float(product.price)
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({'found': False})

@login_required
def api_resolve_alert(request, alert_id):
    """API endpoint to resolve an alert."""
    if request.method == 'POST':
        try:
            alert = StockAlert.objects.get(id=alert_id)
            alert.status = 'RESOLVED'
            alert.resolved_at = timezone.now()
            alert.resolved_by = request.user
            alert.save()
            return JsonResponse({'success': True})
        except StockAlert.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Alert not found'})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# Enhanced existing views
@login_required
def product_list(request):
    """Enhanced product list with real-time filtering and search."""
    products = Product.objects.select_related('category', 'supplier').filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Apply filters
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(sku__icontains=search) | 
            Q(barcode__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if stock_status == 'low':
        products = products.filter(quantity__lte=F('minimum_stock'))
    elif stock_status == 'ok':
        products = products.filter(quantity__gt=F('minimum_stock'))
    elif stock_status == 'out':
        products = products.filter(quantity=0)
    
    # Pagination
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'inventory/product_list.html', context)

@login_required
def alerts_view(request):
    """View for managing stock alerts."""
    alerts = StockAlert.objects.select_related('product').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', 'ACTIVE')
    if status:
        alerts = alerts.filter(status=status)
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'alerts': page_obj,
        'current_status': status,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'inventory/alerts.html', context)

# Keep all existing views from the original file
@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True)
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
        category.is_active = False
        category.save()
        messages.success(request, 'Catégorie supprimée avec succès.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/category_confirm_delete.html', {'category': category})

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
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
        form = ProductForm(request.POST, request.FILES, instance=product)
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
        product.is_active = False
        product.save()
        messages.success(request, 'Produit supprimé avec succès.')
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

@login_required
@transaction.atomic
def stock_entry(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'IN'
            movement.user = request.user
            movement.save()
            messages.success(request, 'Entrée de stock enregistrée avec succès.')
            return redirect('inventory:stock_history')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/stock_movement_form.html', {
        'form': form,
        'movement_type': 'IN'
    })

@login_required
@transaction.atomic
def stock_exit(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.movement_type = 'OUT'
            movement.user = request.user
            
            # Check stock availability
            if movement.quantity > movement.product.quantity:
                messages.error(request, 'Quantité insuffisante en stock.')
                return render(request, 'inventory/stock_movement_form.html', {
                    'form': form,
                    'movement_type': 'OUT'
                })
            
            movement.save()
            messages.success(request, 'Sortie de stock enregistrée avec succès.')
            return redirect('inventory:stock_history')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/stock_movement_form.html', {
        'form': form,
        'movement_type': 'OUT'
    })

@login_required
def stock_history(request):
    # Get filter parameters
    product_id = request.GET.get('product')
    movement_type = request.GET.get('movement_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset
    movements = StockMovement.objects.select_related('product', 'user').order_by('-date')

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
        value=Sum('total_value'))['value'] or 0

    # Pagination
    paginator = Paginator(movements, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all products for the filter dropdown
    products = Product.objects.filter(is_active=True)

    context = {
        'movements': page_obj,
        'products': products,
        'total_movements': total_movements,
        'total_entries': total_entries,
        'total_exits': total_exits,
        'total_value': total_value,
        'query_params': request.GET.urlencode(),
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'inventory/stock_history.html', context)

# Supplier Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.filter(is_active=True)
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
        supplier.is_active = False
        supplier.save()
        messages.success(request, 'Fournisseur supprimé avec succès.')
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/supplier_confirm_delete.html', {'supplier': supplier})

# Statistics and Charts
@login_required
def stock_movement_chart(request):
    """API endpoint for stock movement chart data."""
    period = request.GET.get('period', '30d')
    days = int(period.replace('d', ''))
    
    labels = []
    entries_data = []
    exits_data = []
    
    # Get data for the specified period
    for i in range(days, -1, -1):
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
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    
    return JsonResponse({
        'labels': [cat.name for cat in categories],
        'data': [cat.product_count for cat in categories],
    })

@login_required
def statistics(request):
    """Enhanced statistics view with detailed analytics."""
    # Get date range
    period = request.GET.get('period', '30')
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))

    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d')
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d')

    # Calculate statistics
    total_stock_value = Product.objects.filter(is_active=True).aggregate(
        value=Sum(F('quantity') * F('price')))['value'] or 0

    # Movement statistics
    movements = StockMovement.objects.filter(date__range=[start_date, end_date])
    total_entries = movements.filter(movement_type='IN').count()
    total_exits = movements.filter(movement_type='OUT').count()
    total_entries_value = movements.filter(movement_type='IN').aggregate(
        value=Sum('total_value'))['value'] or 0
    total_exits_value = movements.filter(movement_type='OUT').aggregate(
        value=Sum('total_value'))['value'] or 0

    # Low stock products
    low_stock_products = Product.objects.filter(
        quantity__lte=F('minimum_stock'),
        is_active=True
    ).annotate(stock_value=F('quantity') * F('price'))
    
    low_stock_count = low_stock_products.count()
    total_products = Product.objects.filter(is_active=True).count()

    # Most moved products
    most_moved_products = Product.objects.filter(is_active=True).annotate(
        total_movements=Count('movements', filter=Q(movements__date__range=[start_date, end_date]))
    ).order_by('-total_movements')[:10]

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_stock_value': total_stock_value,
        'total_entries': total_entries,
        'total_exits': total_exits,
        'total_entries_value': total_entries_value,
        'total_exits_value': total_exits_value,
        'low_stock_count': low_stock_count,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'most_moved_products': most_moved_products,
    }
    return render(request, 'inventory/statistics.html', context)

# Export functionality
@login_required
def export_products(request):
    """Export products list to Excel."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Write headers
    headers = ['SKU', 'Nom', 'Code-barres', 'Catégorie', 'Prix', 'Quantité', 'Stock minimum', 'Statut']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Write data
    products = Product.objects.select_related('category').filter(is_active=True)
    for row, product in enumerate(products, 1):
        worksheet.write(row, 0, product.sku)
        worksheet.write(row, 1, product.name)
        worksheet.write(row, 2, product.barcode or '')
        worksheet.write(row, 3, product.category.name)
        worksheet.write(row, 4, float(product.price))
        worksheet.write(row, 5, product.quantity)
        worksheet.write(row, 6, product.minimum_stock)
        worksheet.write(row, 7, product.stock_status)

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
    """Export stock movements to CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=stock_movements.csv'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Produit', 'SKU', 'Type', 'Quantité', 'Prix unitaire', 'Total', 'Utilisateur'])

    movements = StockMovement.objects.select_related('product', 'user').order_by('-date')[:1000]
    for movement in movements:
        writer.writerow([
            movement.date.strftime('%Y-%m-%d %H:%M:%S'),
            movement.product.name,
            movement.product.sku,
            movement.get_movement_type_display(),
            movement.quantity,
            movement.unit_price,
            movement.total_value,
            movement.user.username if movement.user else ''
        ])

    return response