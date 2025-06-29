from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Dashboard
    path('', views.billing_dashboard, name='dashboard'),
    
    # Company settings
    path('company/', views.company_settings, name='company_settings'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add/', views.invoice_add, name='invoice_add'),
    path('invoices/<uuid:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<uuid:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<uuid:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<uuid:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<uuid:pk>/send/', views.invoice_send, name='invoice_send'),
    path('invoices/<uuid:pk>/duplicate/', views.invoice_duplicate, name='invoice_duplicate'),
    path('invoices/<uuid:pk>/print/', views.invoice_print, name='invoice_print'),
    
    # Payments
    path('invoices/<uuid:invoice_pk>/payments/add/', views.payment_add, name='payment_add'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    
    # Templates
    path('templates/', views.template_list, name='template_list'),
    path('templates/add/', views.template_add, name='template_add'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    
    # Reports
    path('reports/', views.billing_reports, name='reports'),
    path('reports/export/', views.export_reports, name='export_reports'),
    path('export/invoices/', views.export_invoices, name='export_invoices'),
    
    # API endpoints
    path('api/customer-info/<int:customer_id>/', views.api_customer_info, name='api_customer_info'),
    path('api/product-info/<int:product_id>/', views.api_product_info, name='api_product_info'),
    path('api/invoice-stats/', views.api_invoice_stats, name='api_invoice_stats'),
    path('api/revenue-chart/', views.api_revenue_chart, name='api_revenue_chart'),
    path('api/top-customers/', views.api_top_customers, name='api_top_customers'),
    path('api/top-products/', views.api_top_products, name='api_top_products'),
    path('api/payment-methods/', views.api_payment_methods, name='api_payment_methods'),
    path('api/monthly-comparison/', views.api_monthly_comparison, name='api_monthly_comparison'),
]