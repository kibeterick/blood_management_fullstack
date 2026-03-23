"""
Email Notification Service
Handles email notifications using Django email backend
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import NotificationLog, NotificationPreference, CustomUser
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Handle email notifications using Django email backend"""
    
    @staticmethod
    def send_urgent_blood_notification(donors, blood_type, urgency='high'):
        """Send urgent blood need notification to matching donors"""
        subject = f"🩸 Urgent: {blood_type} Blood Needed"
        
        sent_count = 0
        for donor in donors:
            if not donor.user:
                continue
            
            # Check preferences
            prefs = NotificationPreference.objects.filter(user=donor.user).first()
            if prefs and not prefs.urgent_blood_email:
                continue
            
            context = {
                'donor': donor,
                'blood_type': blood_type,
                'urgency': urgency,
                'contact_phone': getattr(settings, 'BLOOD_BANK_CONTACT', 'Blood Bank'),
            }
            
            try:
                html_message = render_to_string('notifications/urgent_blood_email.html', context)
                plain_message = render_to_string('notifications/urgent_blood_email.txt', context)
                
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[donor.email]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send()
                
                # Log success
                NotificationLog.objects.create(
                    user=donor.user,
                    notification_type='urgent_blood',
                    channel='email',
                    recipient=donor.email,
                    subject=subject,
                    message=plain_message,
                    status='sent',
                    sent_at=timezone.now()
                )
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send urgent blood email to {donor.email}: {str(e)}")
                # Log failure
                NotificationLog.objects.create(
                    user=donor.user,
                    notification_type='urgent_blood',
                    channel='email',
                    recipient=donor.email,
                    subject=subject,
                    message=plain_message,
                    status='failed',
                    error_message=str(e)
                )
        
        logger.info(f"Sent {sent_count} urgent blood notifications for {blood_type}")
        return sent_count
    
    @staticmethod
    def send_low_stock_alert(inventory):
        """Send low stock alert to all admin users"""
        # Get all admin users
        admin_users = CustomUser.objects.filter(role='admin')
        
        if not admin_users.exists():
            logger.warning("No admin users found to send low stock alert")
            return False
        
        subject = f"⚠️ Low Stock Alert: {inventory.blood_type} Blood"
        
        context = {
            'inventory': inventory,
            'blood_type': inventory.blood_type,
            'current_quantity': inventory.units_available,
            'threshold': inventory.minimum_threshold,
            'status': inventory.get_status(),
        }
        
        sent_count = 0
        for admin in admin_users:
            # Check preferences
            prefs = NotificationPreference.objects.filter(user=admin).first()
            if prefs and not prefs.low_stock_email:
                continue
            
            try:
                html_message = render_to_string('notifications/low_stock_alert.html', context)
                plain_message = render_to_string('notifications/low_stock_alert.txt', context)
                
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[admin.email]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send()
                
                # Log success
                NotificationLog.objects.create(
                    user=admin,
                    notification_type='low_stock',
                    channel='email',
                    recipient=admin.email,
                    subject=subject,
                    message=plain_message,
                    status='sent',
                    sent_at=timezone.now()
                )
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send low stock alert to {admin.email}: {str(e)}")
                # Log failure
                NotificationLog.objects.create(
                    user=admin,
                    notification_type='low_stock',
                    channel='email',
                    recipient=admin.email,
                    subject=subject,
                    message=plain_message,
                    status='failed',
                    error_message=str(e)
                )
        
        logger.info(f"Sent {sent_count} low stock alerts for {inventory.blood_type}")
        return sent_count > 0
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """Send appointment booking confirmation with calendar attachment"""
        if not appointment.user:
            return False
        
        prefs = NotificationPreference.objects.filter(user=appointment.user).first()
        if prefs and not prefs.booking_confirmation_email:
            return False
        
        subject = f"✅ Appointment Confirmed - {appointment.appointment_date}"
        
        context = {
            'appointment': appointment,
            'donor': appointment.donor,
        }
        
        try:
            html_message = render_to_string('notifications/appointment_confirmation.html', context)
            plain_message = render_to_string('notifications/appointment_confirmation.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[appointment.donor.email]
            )
            msg.attach_alternative(html_message, "text/html")
            
            # Attach ICS calendar file
            try:
                from .utils import generate_ics_file
                ics_content = generate_ics_file(appointment)
                msg.attach('appointment.ics', ics_content, 'text/calendar')
            except Exception as e:
                logger.warning(f"Failed to attach ICS file: {str(e)}")
            
            msg.send()
            
            NotificationLog.objects.create(
                user=appointment.user,
                notification_type='booking_confirmation',
                channel='email',
                recipient=appointment.donor.email,
                subject=subject,
                message=plain_message,
                status='sent',
                sent_at=timezone.now()
            )
            logger.info(f"Sent appointment confirmation to {appointment.donor.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send appointment confirmation to {appointment.donor.email}: {str(e)}")
            NotificationLog.objects.create(
                user=appointment.user,
                notification_type='booking_confirmation',
                channel='email',
                recipient=appointment.donor.email,
                subject=subject,
                message=plain_message,
                status='failed',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """Send appointment reminder email (24 hours before)"""
        if not appointment.user:
            return False
        
        prefs = NotificationPreference.objects.filter(user=appointment.user).first()
        if prefs and not prefs.appointment_reminder_email:
            return False
        
        subject = f"🩸 Reminder: Blood Donation Appointment Tomorrow"
        
        context = {
            'appointment': appointment,
            'donor': appointment.donor,
        }
        
        try:
            html_message = render_to_string('notifications/appointment_confirmation.html', context)
            plain_message = render_to_string('notifications/appointment_confirmation.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[appointment.donor.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()
            
            NotificationLog.objects.create(
                user=appointment.user,
                notification_type='appointment_reminder',
                channel='email',
                recipient=appointment.donor.email,
                subject=subject,
                message=plain_message,
                status='sent',
                sent_at=timezone.now()
            )
            logger.info(f"Sent appointment reminder to {appointment.donor.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send appointment reminder to {appointment.donor.email}: {str(e)}")
            NotificationLog.objects.create(
                user=appointment.user,
                notification_type='appointment_reminder',
                channel='email',
                recipient=appointment.donor.email,
                subject=subject,
                message=plain_message,
                status='failed',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def send_request_status_notification(blood_request, status):
        """Send blood request status update notification"""
        subject = f"Blood Request {status.title()} - {blood_request.blood_type}"
        
        prefs = NotificationPreference.objects.filter(user=blood_request.requester).first()
        if prefs and not prefs.request_status_email:
            return False
        
        context = {
            'request': blood_request,
            'status': status,
        }
        
        try:
            html_message = render_to_string('notifications/request_status_email.html', context)
            plain_message = render_to_string('notifications/request_status_email.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[blood_request.requester.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send()
            
            NotificationLog.objects.create(
                user=blood_request.requester,
                notification_type='request_status',
                channel='email',
                recipient=blood_request.requester.email,
                subject=subject,
                message=plain_message,
                status='sent',
                sent_at=timezone.now()
            )
            logger.info(f"Sent request status notification to {blood_request.requester.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send request status notification to {blood_request.requester.email}: {str(e)}")
            NotificationLog.objects.create(
                user=blood_request.requester,
                notification_type='request_status',
                channel='email',
                recipient=blood_request.requester.email,
                subject=subject,
                message=plain_message,
                status='failed',
                error_message=str(e)
            )
            return False
