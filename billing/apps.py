from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'
    verbose_name = 'Facturation'

    def ready(self):
        """
        Initialize app configurations when the app is ready.
        """
        try:
            # Import signals
            import billing.signals  # noqa
        except ImportError:
            pass