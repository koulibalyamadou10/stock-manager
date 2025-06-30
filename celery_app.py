import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_manager.settings')

app = Celery('stock_manager')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'daily-stock-alerts': {
        'task': 'inventory.tasks.daily_stock_alerts',
        'schedule': 86400.0,  # Every 24 hours
    },
    'weekly-backup': {
        'task': 'inventory.tasks.weekly_backup',
        'schedule': 604800.0,  # Every 7 days
    },
    'update-reorder-points': {
        'task': 'inventory.tasks.update_reorder_points',
        'schedule': 259200.0,  # Every 3 days
    },
    'cleanup-old-alerts': {
        'task': 'inventory.tasks.cleanup_old_alerts',
        'schedule': 86400.0,  # Every 24 hours
    },
    'generate-sales-insights': {
        'task': 'inventory.tasks.generate_sales_insights',
        'schedule': 43200.0,  # Every 12 hours
    },
}

app.conf.timezone = 'Africa/Conakry'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')