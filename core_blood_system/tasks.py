"""
Celery Tasks for Blood Management System
Scheduled tasks for notifications and inventory management
"""
from celery import shared_task
from datetime import date, timedelta
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_appointment_reminders():
    """
    Send reminders for appointments 24 hours away
    Runs daily at 9:00 AM
    """
    from .models import DonationAppointment
    from .email_notifications import EmailNotificationService
    from .sms_notifications import SMSNotificationService
    
    tomorrow = date.today() + timedelta(days=1)
    
    # Get appointments for tomorrow that haven't had reminders sent
    appointments = DonationAppointment.objects.filter(
        appointment_date=tomorrow,
        status='scheduled',
        reminder_sent=False
    )
    
    sent_count = 0
    email_count = 0
    sms_count = 0
    
    for appointment in appointments:
        try:
            # Send email reminder
            if EmailNotificationService.send_appointment_reminder(appointment):
                email_count += 1
            
            # Send SMS reminder
            if SMSNotificationService.send_appointment_reminder(appointment):
                sms_count += 1
            
            # Mark reminder as sent
            appointment.reminder_sent = True
            appointment.save()
            sent_count += 1
            
        except Exception as e:
            logger.error(f"Failed to send reminder for appointment {appointment.id}: {str(e)}")
    
    result = f"Sent {sent_count} appointment reminders ({email_count} emails, {sms_count} SMS)"
    logger.info(result)
    return result


@shared_task
def mark_expired_units():
    """
    Mark expired blood units daily
    Runs daily at midnight
    """
    # Disabled - requires InventoryManager enhancement
    logger.info("mark_expired_units task disabled - enhancement not deployed")
    return "Task disabled"
    # from .inventory_manager import InventoryManager
    # 
    # try:
    #     expired_count = InventoryManager.mark_expired_units()
    #     result = f"Marked {expired_count} blood units as expired"
    #     logger.info(result)
    #     return result
    # except Exception as e:
    #     logger.error(f"Failed to mark expired units: {str(e)}")
    #     return f"Error: {str(e)}"


@shared_task
def check_low_stock():
    """
    Check inventory thresholds and send alerts to admins if below threshold
    Respects 24-hour notification limit
    Runs daily at 8:00 AM
    """
    # Disabled - requires enhanced BloodInventory model fields
    logger.info("check_low_stock task disabled - enhancement not deployed")
    return "Task disabled"
    # from .models import BloodInventory, CustomUser
    # from .email_notifications import EmailNotificationService
    # 
    # try:
    #     low_stock_items = []
    #     
    #     # Check all inventory items
    #     for inventory in BloodInventory.objects.all():
    #         status = inventory.get_status()
    #         
    #         # Check if stock is low or critical
    #         if status in ['low', 'critical']:
    #             # Check if we haven't sent an alert in the last 24 hours
    #             if not inventory.alert_sent_at or (timezone.now() - inventory.alert_sent_at).total_seconds() >= 86400:
    #                 low_stock_items.append(inventory)
    #     
    #     # Send alerts for low stock items
    #     alert_count = 0
    #     for inventory in low_stock_items:
    #         if EmailNotificationService.send_low_stock_alert(inventory):
    #             inventory.alert_sent_at = timezone.now()
    #             inventory.save()
    #             alert_count += 1
    #     
    #     result = f"Sent {alert_count} low stock alerts for {len(low_stock_items)} blood types"
    #     logger.info(result)
    #     return result
    #     
    # except Exception as e:
    #     logger.error(f"Failed to check low stock: {str(e)}")
    #     return f"Error: {str(e)}"
