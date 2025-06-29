from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Sum, Count, Q, Avg, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import csv
import json
import xlsxwriter
from io import BytesIO
from .models import (
    Company, Customer, Invoice, InvoiceItem, InvoiceTemplate, 
    Payment, EmailLog
)
from .forms import (
    CompanyForm, CustomerForm, InvoiceForm, InvoiceItemFormSet,
    PaymentForm, InvoiceTemplateForm, EmailInvoiceForm
)
from .utils import generate_invoice_pdf, send_invoice_email, get_invoice_statistics

@login_required
def billing_dashboard(request):
    """Dashboard de facturation avec statistiques"""
    # Statistiques générales
    stats = get_invoice_statistics()
    
    # Factures récentes
    recent_invoices = Invoice.objects.select_related('customer').order_by('-created_at')[:10]
    
    # Factures en retard
    overdue_invoices = Invoice.objects.filter(
        status='overdue'
    ).select_related('customer').order_by('due_date')[:5]
    
    # Paiements récents
    recent_payments = Payment.objects.select_related(
        'invoice', 'invoice__customer'
    ).order_by('-created_at')[:10]
    
    # Graphique des revenus (30 derniers jours)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    daily_revenue = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        revenue = Invoice.objects.filter(
            issue_date=date,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        daily_revenue.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue)
        })
    
    context = {
        'stats': stats,
        'recent_invoices': recent_invoices,
        'overdue_invoices': overdue_invoices,
        'recent_payments': recent_payments,
        'daily_revenue': json.dumps(daily_revenue),
    }
    return render(request, 'billing/dashboard.html', context)

@login_required
def company_settings(request):
    """Paramètres de l'entreprise"""
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informations de l\'entreprise mises à jour.')
            return redirect('billing:company_settings')
    else:
        form = CompanyForm(instance=company)
    
    return render(request, 'billing/company_settings.html', {'form': form})

# Customer Views
@login_required
def customer_list(request):
    """Liste des clients"""
    customers = Customer.objects.filter(is_active=True).order_by('name')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(customers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'search': search,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'billing/customer_list.html', context)

@login_required
def customer_add(request):
    """Ajouter un client"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client ajouté avec succès.')
            return redirect('billing:customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'billing/customer_form.html', {'form': form})

@login_required
def customer_edit(request, pk):
    """Modifier un client"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client modifié avec succès.')
            return redirect('billing:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'billing/customer_form.html', {'form': form, 'customer': customer})

@login_required
def customer_delete(request, pk):
    """Supprimer un client"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.is_active = False
        customer.save()
        messages.success(request, 'Client supprimé avec succès.')
        return redirect('billing:customer_list')
    
    return render(request, 'billing/customer_confirm_delete.html', {'customer': customer})

# Invoice Views
@login_required
def invoice_list(request):
    """Liste des factures"""
    invoices = Invoice.objects.select_related('customer').order_by('-created_at')
    
    # Filters
    status = request.GET.get('status', '')
    customer_id = request.GET.get('customer', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    if status:
        invoices = invoices.filter(status=status)
    if customer_id:
        invoices = invoices.filter(customer_id=customer_id)
    if start_date:
        invoices = invoices.filter(issue_date__gte=start_date)
    if end_date:
        invoices = invoices.filter(issue_date__lte=end_date)
    
    # Pagination
    paginator = Paginator(invoices, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get customers for filter
    customers = Customer.objects.filter(is_active=True).order_by('name')
    
    context = {
        'invoices': page_obj,
        'customers': customers,
        'current_status': status,
        'current_customer': customer_id,
        'start_date': start_date,
        'end_date': end_date,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'billing/invoice_list.html', context)

@login_required
@transaction.atomic
def invoice_add(request):
    """Ajouter une facture"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            
            formset.instance = invoice
            formset.save()
            
            # Recalculate totals
            invoice.calculate_totals()
            invoice.save()
            
            messages.success(request, f'Facture {invoice.invoice_number} créée avec succès.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Nouvelle facture'
    }
    return render(request, 'billing/invoice_form.html', context)

@login_required
def invoice_detail(request, pk):
    """Détail d'une facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = invoice.payments.order_by('-payment_date')
    email_logs = invoice.email_logs.order_by('-sent_at')[:5]
    
    # Calculate payment summary
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    remaining_amount = invoice.total_amount - total_paid
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'email_logs': email_logs,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
    }
    return render(request, 'billing/invoice_detail.html', context)

@login_required
@transaction.atomic
def invoice_edit(request, pk):
    """Modifier une facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status == 'paid':
        messages.error(request, 'Impossible de modifier une facture payée.')
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Recalculate totals
            invoice.calculate_totals()
            invoice.save()
            
            messages.success(request, f'Facture {invoice.invoice_number} modifiée avec succès.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    
    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': f'Modifier facture {invoice.invoice_number}'
    }
    return render(request, 'billing/invoice_form.html', context)

@login_required
def invoice_delete(request, pk):
    """Supprimer une facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status == 'paid':
        messages.error(request, 'Impossible de supprimer une facture payée.')
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Facture {invoice_number} supprimée avec succès.')
        return redirect('billing:invoice_list')
    
    return render(request, 'billing/invoice_confirm_delete.html', {'invoice': invoice})

@login_required
def invoice_pdf(request, pk):
    """Générer le PDF d'une facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    try:
        pdf_content = generate_invoice_pdf(invoice)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="facture_{invoice.invoice_number}.pdf"'
        
        return response
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('billing:invoice_detail', pk=invoice.pk)

@login_required
def invoice_send(request, pk):
    """Envoyer une facture par email"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if not invoice.customer.email:
        messages.error(request, 'Le client n\'a pas d\'adresse email.')
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    if request.method == 'POST':
        form = EmailInvoiceForm(invoice, request.POST)
        if form.is_valid():
            success, message = send_invoice_email(
                invoice=invoice,
                recipient=form.cleaned_data['recipient'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                send_copy=form.cleaned_data['send_copy'],
                user=request.user
            )
            
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = EmailInvoiceForm(invoice)
    
    return render(request, 'billing/invoice_send.html', {'form': form, 'invoice': invoice})

@login_required
def invoice_duplicate(request, pk):
    """Dupliquer une facture"""
    original_invoice = get_object_or_404(Invoice, pk=pk)
    
    with transaction.atomic():
        # Create new invoice
        new_invoice = Invoice.objects.create(
            customer=original_invoice.customer,
            template=original_invoice.template,
            payment_terms=original_invoice.payment_terms,
            tax_rate=original_invoice.tax_rate,
            discount_rate=original_invoice.discount_rate,
            reference=original_invoice.reference,
            notes=original_invoice.notes,
            created_by=request.user,
            status='draft'
        )
        
        # Copy invoice items
        for item in original_invoice.items.all():
            InvoiceItem.objects.create(
                invoice=new_invoice,
                product=item.product,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                order=item.order
            )
        
        # Recalculate totals
        new_invoice.calculate_totals()
        new_invoice.save()
    
    messages.success(request, f'Facture dupliquée. Nouvelle facture: {new_invoice.invoice_number}')
    return redirect('billing:invoice_edit', pk=new_invoice.pk)

@login_required
def invoice_print(request, pk):
    """Version imprimable de la facture"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    context = {
        'invoice': invoice,
        'company': company,
    }
    return render(request, 'billing/invoice_print.html', context)

# Payment Views
@login_required
def payment_add(request, invoice_pk):
    """Ajouter un paiement"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    # Calculate remaining amount
    total_paid = invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
    remaining_amount = invoice.total_amount - total_paid
    
    if remaining_amount <= 0:
        messages.info(request, 'Cette facture est déjà entièrement payée.')
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            
            # Check if payment amount doesn't exceed remaining amount
            if payment.amount > remaining_amount:
                messages.error(request, f'Le montant ne peut pas dépasser le solde restant: {remaining_amount:,.0f} GNF')
                return render(request, 'billing/payment_form.html', {
                    'form': form, 
                    'invoice': invoice, 
                    'remaining_amount': remaining_amount
                })
            
            payment.save()
            messages.success(request, 'Paiement enregistré avec succès.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = PaymentForm(initial={'amount': remaining_amount})
    
    return render(request, 'billing/payment_form.html', {
        'form': form, 
        'invoice': invoice, 
        'remaining_amount': remaining_amount
    })

@login_required
def payment_list(request):
    """Liste des paiements"""
    payments = Payment.objects.select_related('invoice', 'invoice__customer').order_by('-payment_date')
    
    # Filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    payment_method = request.GET.get('payment_method', '')
    
    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    if payment_method:
        payments = payments.filter(payment_method=payment_method)
    
    # Pagination
    paginator = Paginator(payments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'current_payment_method': payment_method,
        'payment_methods': Payment.PAYMENT_METHODS,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'billing/payment_list.html', context)

@login_required
def payment_edit(request, pk):
    """Modifier un paiement"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paiement modifié avec succès.')
            return redirect('billing:invoice_detail', pk=payment.invoice.pk)
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'billing/payment_form.html', {
        'form': form, 
        'payment': payment,
        'invoice': payment.invoice
    })

@login_required
def payment_delete(request, pk):
    """Supprimer un paiement"""
    payment = get_object_or_404(Payment, pk=pk)
    invoice = payment.invoice
    
    if request.method == 'POST':
        payment.delete()
        
        # Update invoice status if needed
        total_paid = invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
        if total_paid < invoice.total_amount and invoice.status == 'paid':
            invoice.status = 'sent'
            invoice.save()
        
        messages.success(request, 'Paiement supprimé avec succès.')
        return redirect('billing:invoice_detail', pk=invoice.pk)
    
    return render(request, 'billing/payment_confirm_delete.html', {'payment': payment})

# Template Views
@login_required
def template_list(request):
    """Liste des modèles de factures"""
    templates = InvoiceTemplate.objects.order_by('-is_default', 'name')
    return render(request, 'billing/template_list.html', {'templates': templates})

@login_required
def template_add(request):
    """Ajouter un modèle de facture"""
    if request.method == 'POST':
        form = InvoiceTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modèle de facture créé avec succès.')
            return redirect('billing:template_list')
    else:
        form = InvoiceTemplateForm()
    
    return render(request, 'billing/template_form.html', {'form': form})

@login_required
def template_edit(request, pk):
    """Modifier un modèle de facture"""
    template = get_object_or_404(InvoiceTemplate, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modèle de facture modifié avec succès.')
            return redirect('billing:template_list')
    else:
        form = InvoiceTemplateForm(instance=template)
    
    return render(request, 'billing/template_form.html', {'form': form, 'template': template})

@login_required
def template_delete(request, pk):
    """Supprimer un modèle de facture"""
    template = get_object_or_404(InvoiceTemplate, pk=pk)
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Modèle de facture supprimé avec succès.')
        return redirect('billing:template_list')
    
    return render(request, 'billing/template_confirm_delete.html', {'template': template})

# Reports
@login_required
def billing_reports(request):
    """Rapports de facturation"""
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Get statistics
    stats = get_invoice_statistics(start_date, end_date)
    
    # Top customers
    top_customers = Customer.objects.filter(
        invoices__issue_date__range=[start_date, end_date],
        invoices__status='paid'
    ).annotate(
        total_amount=Sum('invoices__total_amount'),
        invoice_count=Count('invoices')
    ).order_by('-total_amount')[:10]
    
    # Monthly revenue
    monthly_revenue = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        revenue = Invoice.objects.filter(
            issue_date__gte=current_date,
            issue_date__lt=next_month,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_revenue.append({
            'month': current_date.strftime('%Y-%m'),
            'revenue': float(revenue)
        })
        current_date = next_month
    
    context = {
        'stats': stats,
        'top_customers': top_customers,
        'monthly_revenue': json.dumps(monthly_revenue),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'billing/reports.html', context)

@login_required
def export_invoices(request):
    """Exporter les factures en CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=factures.csv'
    
    writer = csv.writer(response)
    writer.writerow([
        'Numéro', 'Client', 'Date émission', 'Date échéance', 
        'Statut', 'Sous-total', 'TVA', 'Total', 'Référence'
    ])
    
    invoices = Invoice.objects.select_related('customer').order_by('-created_at')[:1000]
    for invoice in invoices:
        writer.writerow([
            invoice.invoice_number,
            invoice.customer.name,
            invoice.issue_date.strftime('%Y-%m-%d'),
            invoice.due_date.strftime('%Y-%m-%d'),
            invoice.get_status_display(),
            invoice.subtotal,
            invoice.tax_amount,
            invoice.total_amount,
            invoice.reference or ''
        ])
    
    return response

# API Endpoints
@login_required
def api_customer_info(request, customer_id):
    """API pour récupérer les infos d'un client"""
    try:
        customer = Customer.objects.get(pk=customer_id)
        return JsonResponse({
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'tax_number': customer.tax_number,
        })
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Client non trouvé'}, status=404)

@login_required
def api_product_info(request, product_id):
    """API pour récupérer les infos d'un produit"""
    try:
        from inventory.models import Product
        product = Product.objects.get(pk=product_id)
        return JsonResponse({
            'name': product.name,
            'price': float(product.price),
            'description': product.description,
        })
    except:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)

@login_required
def api_invoice_stats(request):
    """API pour les statistiques de facturation"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    stats = get_invoice_statistics(start_date, end_date)
    
    # Calculate additional metrics
    if stats['total_invoices'] > 0:
        stats['average_invoice'] = stats['total_amount'] / stats['total_invoices']
        stats['collection_rate'] = (stats['paid_invoices'] / stats['total_invoices']) * 100
    else:
        stats['average_invoice'] = 0
        stats['collection_rate'] = 0
    
    # Calculate change vs previous period
    if start_date and end_date:
        period_days = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_days)
        prev_end = start_date
        
        prev_stats = get_invoice_statistics(prev_start, prev_end)
        
        if prev_stats['total_amount'] > 0:
            stats['revenue_change'] = ((stats['total_amount'] - prev_stats['total_amount']) / prev_stats['total_amount']) * 100
        else:
            stats['revenue_change'] = 0
    else:
        stats['revenue_change'] = 0
    
    return JsonResponse(stats)

@login_required
def api_revenue_chart(request):
    """API pour le graphique des revenus"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    labels = []
    revenue_data = []
    
    current_date = start_date
    while current_date <= end_date:
        labels.append(current_date.strftime('%d/%m'))
        
        revenue = Invoice.objects.filter(
            issue_date=current_date,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        revenue_data.append(float(revenue))
        current_date += timedelta(days=1)
    
    return JsonResponse({
        'labels': labels,
        'revenue': revenue_data
    })

@login_required
def api_top_customers(request):
    """API pour les meilleurs clients"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    customers = Customer.objects.filter(is_active=True)
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        customers = customers.filter(
            invoices__issue_date__range=[start_date, end_date],
            invoices__status='paid'
        )
    
    customers = customers.annotate(
        total_amount=Sum('invoices__total_amount', filter=Q(invoices__status='paid'))
    ).order_by('-total_amount')[:10]
    
    return JsonResponse({
        'labels': [customer.name for customer in customers],
        'data': [float(customer.total_amount or 0) for customer in customers]
    })

@login_required
def api_top_products(request):
    """API pour les produits les plus vendus"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    from inventory.models import Product
    
    products = Product.objects.filter(is_active=True)
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get products sold in invoice items
        products = products.filter(
            invoiceitem__invoice__issue_date__range=[start_date, end_date],
            invoiceitem__invoice__status='paid'
        ).annotate(
            quantity_sold=Sum('invoiceitem__quantity'),
            revenue=Sum(F('invoiceitem__quantity') * F('invoiceitem__unit_price')),
            avg_price=Avg('invoiceitem__unit_price')
        ).order_by('-revenue')[:10]
    else:
        products = products.annotate(
            quantity_sold=Sum('invoiceitem__quantity'),
            revenue=Sum(F('invoiceitem__quantity') * F('invoiceitem__unit_price')),
            avg_price=Avg('invoiceitem__unit_price')
        ).order_by('-revenue')[:10]
    
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'quantity_sold': product.quantity_sold or 0,
            'revenue': float(product.revenue or 0),
            'avg_price': float(product.avg_price or 0)
        })
    
    return data

@login_required
def api_payment_methods(request):
    """API pour les méthodes de paiement"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    payments = Payment.objects.all()
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        payments = payments.filter(payment_date__range=[start_date, end_date])
    
    # Group by payment method
    methods = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    data = []
    for method in methods:
        percentage = (method['total'] / total_amount * 100) if total_amount > 0 else 0
        data.append({
            'method': method['payment_method'],
            'display_name': dict(Payment.PAYMENT_METHODS)[method['payment_method']],
            'total': float(method['total']),
            'count': method['count'],
            'percentage': round(percentage, 1)
        })
    
    return JsonResponse(data, safe=False)

@login_required
def api_monthly_comparison(request):
    """API pour la comparaison mensuelle"""
    # Get last 12 months
    end_date = timezone.now().date()
    start_date = end_date.replace(day=1) - timedelta(days=365)
    
    labels = []
    revenue_data = []
    invoice_data = []
    
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        labels.append(current_date.strftime('%b %Y'))
        
        # Revenue for the month
        revenue = Invoice.objects.filter(
            issue_date__gte=current_date,
            issue_date__lt=next_month,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Number of invoices for the month
        invoice_count = Invoice.objects.filter(
            issue_date__gte=current_date,
            issue_date__lt=next_month
        ).count()
        
        revenue_data.append(float(revenue))
        invoice_data.append(invoice_count)
        
        current_date = next_month
    
    return JsonResponse({
        'labels': labels,
        'revenue': revenue_data,
        'invoices': invoice_data
    })

@login_required
def export_reports(request):
    """Export reports in various formats"""
    format_type = request.GET.get('format', 'excel')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if format_type == 'excel':
        return export_excel_report(start_date, end_date)
    elif format_type == 'pdf':
        return export_pdf_report(start_date, end_date)
    else:
        return export_csv_report(start_date, end_date)

def export_excel_report(start_date, end_date):
    """Export detailed Excel report"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Create worksheets
    summary_sheet = workbook.add_worksheet('Résumé')
    invoices_sheet = workbook.add_worksheet('Factures')
    payments_sheet = workbook.add_worksheet('Paiements')
    customers_sheet = workbook.add_worksheet('Clients')
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#3b82f6',
        'font_color': 'white',
        'border': 1
    })
    
    currency_format = workbook.add_format({'num_format': '#,##0'})
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    
    # Summary sheet
    stats = get_invoice_statistics(start_date, end_date)
    
    summary_sheet.write('A1', 'Rapport de Facturation', header_format)
    summary_sheet.write('A3', 'Période:', header_format)
    summary_sheet.write('B3', f"{start_date} - {end_date}" if start_date and end_date else "Toutes périodes")
    
    summary_sheet.write('A5', 'Métrique', header_format)
    summary_sheet.write('B5', 'Valeur', header_format)
    
    metrics = [
        ('Total Factures', stats['total_invoices']),
        ('Chiffre d\'affaires', stats['total_amount']),
        ('Factures Payées', stats['paid_invoices']),
        ('Montant Encaissé', stats['paid_amount']),
        ('Factures en Attente', stats['pending_invoices']),
        ('Montant en Attente', stats['pending_amount']),
    ]
    
    for i, (metric, value) in enumerate(metrics, 6):
        summary_sheet.write(f'A{i}', metric)
        if 'Montant' in metric or 'affaires' in metric:
            summary_sheet.write(f'B{i}', value, currency_format)
        else:
            summary_sheet.write(f'B{i}', value)
    
    # Invoices sheet
    invoices = Invoice.objects.select_related('customer').order_by('-created_at')
    if start_date and end_date:
        invoices = invoices.filter(issue_date__range=[start_date, end_date])
    
    invoice_headers = ['Numéro', 'Client', 'Date Émission', 'Date Échéance', 'Statut', 'Total']
    for col, header in enumerate(invoice_headers):
        invoices_sheet.write(0, col, header, header_format)
    
    for row, invoice in enumerate(invoices[:1000], 1):
        invoices_sheet.write(row, 0, invoice.invoice_number)
        invoices_sheet.write(row, 1, invoice.customer.name)
        invoices_sheet.write(row, 2, invoice.issue_date, date_format)
        invoices_sheet.write(row, 3, invoice.due_date, date_format)
        invoices_sheet.write(row, 4, invoice.get_status_display())
        invoices_sheet.write(row, 5, float(invoice.total_amount), currency_format)
    
    # Auto-adjust column widths
    for sheet in [summary_sheet, invoices_sheet, payments_sheet, customers_sheet]:
        sheet.set_column('A:Z', 15)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=rapport_facturation.xlsx'
    return response

def export_csv_report(start_date, end_date):
    """Export CSV report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=rapport_facturation.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Numéro', 'Client', 'Date Émission', 'Date Échéance', 'Statut', 'Total'])
    
    invoices = Invoice.objects.select_related('customer').order_by('-created_at')
    if start_date and end_date:
        invoices = invoices.filter(issue_date__range=[start_date, end_date])
    
    for invoice in invoices[:1000]:
        writer.writerow([
            invoice.invoice_number,
            invoice.customer.name,
            invoice.issue_date.strftime('%Y-%m-%d'),
            invoice.due_date.strftime('%Y-%m-%d'),
            invoice.get_status_display(),
            float(invoice.total_amount)
        ])
    
    return response