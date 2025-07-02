from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Landing page (site vitrine) - page d'accueil
    path('', include('landing.urls')),
    
    # Subscriptions app URLs
    path('subscriptions/', include('subscriptions.urls')),
    
    # Inventory app URLs
    path('inventory/', include('inventory.urls')),
    
    # Billing app URLs
    path('billing/', include('billing.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = 'StockManager Pro Administration'
admin.site.site_title = 'StockManager Pro Admin'
admin.site.index_title = 'Tableau de bord administration'