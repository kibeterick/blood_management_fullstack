"""
Django Management Command: Mark Expired Blood Units
Alternative to Celery task for PythonAnywhere scheduled tasks
"""
from django.core.management.base import BaseCommand
from core_blood_system.inventory_manager import InventoryManager


class Command(BaseCommand):
    help = 'Mark expired blood units and update inventory counts'

    def handle(self, *args, **options):
        try:
            expired_count = InventoryManager.mark_expired_units()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {expired_count} blood units as expired'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to mark expired units: {str(e)}')
            )
