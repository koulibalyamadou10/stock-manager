from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'Gestion de Stock'

    def ready(self):
        """
        Initialize app configurations when the app is ready.
        This method is called once when Django starts.
        """
        try:
            # Import signals
            import inventory.signals  # noqa

            # Set up any additional configurations
            from django.conf import settings
            
            # Default settings if not already configured
            if not hasattr(settings, 'STOCK_ALERT_THRESHOLD'):
                settings.STOCK_ALERT_THRESHOLD = 10

            if not hasattr(settings, 'ENABLE_STOCK_NOTIFICATIONS'):
                settings.ENABLE_STOCK_NOTIFICATIONS = True

            if not hasattr(settings, 'REPORT_TYPES'):
                settings.REPORT_TYPES = ['daily', 'weekly', 'monthly']

        except ImportError:
            pass
