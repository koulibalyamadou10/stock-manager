from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
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
    
    # AI and Analytics API endpoints
    path('api/sales-predictions/', views.api_sales_predictions, name='api_sales_predictions'),
    path('api/stock-optimization/', views.api_stock_optimization, name='api_stock_optimization'),
    path('api/seasonal-trends/', views.api_seasonal_trends, name='api_seasonal_trends'),
    path('api/generate-predictions/', views.api_generate_predictions, name='api_generate_predictions'),
    path('api/ai-insights/', views.api_ai_insights, name='api_ai_insights'),
    path('api/predictive-chart/', views.api_predictive_chart, name='api_predictive_chart'),
    path('api/performance-matrix/', views.api_performance_matrix, name='api_performance_matrix'),
    path('api/seasonal-chart/', views.api_seasonal_chart, name='api_seasonal_chart'),
    path('api/profitability-chart/', views.api_profitability_chart, name='api_profitability_chart'),
    path('api/export-analytics/', views.api_export_analytics, name='api_export_analytics'),
    
    # Export functionality
    path('export/products/', views.export_products, name='export_products'),
    path('export/movements/', views.export_movements, name='export_movements'),
]