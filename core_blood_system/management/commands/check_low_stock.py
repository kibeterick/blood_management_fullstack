"""
Django Management Command: Check Low Stock and Send Alerts
Alternative to Celery task for PythonAnywhere scheduled tasks
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core_blood_system.models import BloodInventory
from core_blood_system.email_notifications import EmailNotificationService


class Command(BaseCommand):
    help = 'Check inventory thresholds and send alerts to admins if below threshold'

    def handle(self, *args, **options):
        try:
            low_stock_items = []
            
            # Check all inventory items
            for inventory in BloodInventory.objects.all():
                status = inventory.get_status()
                
                # Check if stock is low or critical
                if status in ['low', 'critical']:
                    # Check if we haven't sent an alert in the last 24 hours
                    if not inventory.alert_sent_at or (timezone.now() - inventory.alert_sent_at).total_seconds() >= 86400:
                        low_stock_items.append(inventory)
            
            # Send alerts for low stock items
            alert_count = 0
            for inventory in low_stock_items:
                if EmailNotificationService.send_low_stock_alert(inventory):
                    inventory.alert_sent_at = timezone.now()
                    inventory.save()
                    alert_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {alert_count} low stock alerts for {len(low_stock_items)} blood types'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to check low stock: {str(e)}')
            )
