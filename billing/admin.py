from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Company, Customer, Invoice, InvoiceItem, InvoiceTemplate, Payment, EmailLog

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('customer_type', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'header_color', 'font_family', 'created_at')
    list_filter = ('is_default', 'created_at')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_price', 'total')
    readonly_fields = ('total',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('amount', 'payment_date', 'payment_method', 'reference')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'status', 'total_amount', 'issue_date', 'due_date', 'actions')
    list_filter = ('status', 'issue_date', 'due_date', 'created_at')
    search_fields = ('invoice_number', 'customer__name', 'reference')
    readonly_fields = ('invoice_number', 'subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'created_at', 'updated_at')
    inlines = [InvoiceItemInline, PaymentInline]
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('invoice_number', 'customer', 'template', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'payment_terms')
        }),
        ('Montants', {
            'fields': ('subtotal', 'discount_rate', 'discount_amount', 'tax_rate', 'tax_amount', 'total_amount')
        }),
        ('Détails', {
            'fields': ('reference', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at', 'sent_at'),
            'classes': ('collapse',)
        })
    )

    def actions(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="{}">PDF</a> '
                '<a class="button" href="{}">Envoyer</a>',
                reverse('billing:invoice_pdf', args=[obj.pk]),
                reverse('billing:invoice_send', args=[obj.pk])
            )
        return ""
    actions.short_description = "Actions"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method', 'created_by')
    list_filter = ('payment_method', 'payment_date', 'created_at')
    search_fields = ('invoice__invoice_number', 'reference')
    readonly_fields = ('created_at',)

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'recipient', 'subject', 'sent_at', 'success', 'sent_by')
    list_filter = ('success', 'sent_at')
    search_fields = ('invoice__invoice_number', 'recipient', 'subject')
    readonly_fields = ('sent_at',)