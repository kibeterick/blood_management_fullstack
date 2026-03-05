"""
Django Management Command: Send Appointment Reminders
Alternative to Celery task for PythonAnywhere scheduled tasks
"""
from django.core.management.base import BaseCommand
from datetime import date, timedelta
from core_blood_system.models import DonationAppointment
from core_blood_system.email_notifications import EmailNotificationService
from core_blood_system.sms_notifications import SMSNotificationService


class Command(BaseCommand):
    help = 'Send reminders for appointments 24 hours away'

    def handle(self, *args, **options):
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
                self.stdout.write(
                    self.style.ERROR(f'Failed to send reminder for appointment {appointment.id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully sent {sent_count} appointment reminders '
                f'({email_count} emails, {sms_count} SMS)'
            )
        )
