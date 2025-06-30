from django.core.management.base import BaseCommand
from inventory.utils import backup_database
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create a backup of the database'

    def handle(self, *args, **options):
        try:
            backup_file = backup_database()
            if backup_file:
                self.stdout.write(
                    self.style.SUCCESS(f'Database backup created: {backup_file}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to create database backup')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating backup: {str(e)}')
            )
            logger.error(f'Database backup error: {str(e)}')