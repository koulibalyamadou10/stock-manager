from django.core.management.base import BaseCommand
from inventory.utils import send_stock_alerts
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send stock alert notifications for low stock products'

    def handle(self, *args, **options):
        try:
            send_stock_alerts()
            self.stdout.write(
                self.style.SUCCESS('Stock alerts sent successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending stock alerts: {str(e)}')
            )
            logger.error(f'Stock alerts command error: {str(e)}')