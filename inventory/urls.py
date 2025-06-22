from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Stock Movements
    path('stock/entry/', views.stock_entry, name='stock_entry'),
    path('stock/exit/', views.stock_exit, name='stock_exit'),
    path('stock/history/', views.stock_history, name='stock_history'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Alerts
    path('alerts/', views.alerts_view, name='alerts'),
    
    # Statistics
    path('statistics/', views.statistics, name='statistics'),
    
    # API endpoints
    path('api/alerts/', views.api_alerts, name='api_alerts'),
    path('api/alerts/<int:alert_id>/resolve/', views.api_resolve_alert, name='api_resolve_alert'),
    path('api/alerts-count/', views.api_alerts_count, name='api_alerts_count'),
    path('api/recent-movements/', views.api_recent_movements, name='api_recent_movements'),
    path('api/search-products/', views.api_search_products, name='api_search_products'),
    path('api/search-by-barcode/', views.api_search_by_barcode, name='api_search_by_barcode'),
    path('api/stock-movement-chart/', views.stock_movement_chart, name='stock_movement_chart'),
    path('api/product-category-chart/', views.product_category_chart, name='product_category_chart'),
    
    # Export functionality
    path('export/products/', views.export_products, name='export_products'),
    path('export/movements/', views.export_movements, name='export_movements'),
]