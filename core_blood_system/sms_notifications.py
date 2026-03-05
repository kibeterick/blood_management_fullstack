"""
SMS Notification Service
Handles SMS notifications via Twilio or Africa's Talking
"""
from django.conf import settings
from django.utils import timezone
from .models import NotificationLog, NotificationPreference
import logging

logger = logging.getLogger(__name__)


class SMSNotificationService:
    """Handle SMS notifications via Twilio or Africa's Talking"""
    
    @staticmethod
    def get_provider():
        """Get configured SMS provider"""
        return getattr(settings, 'SMS_PROVIDER', None)
    
    @staticmethod
    def is_configured():
        """Check if SMS service is properly configured"""
        provider = SMSNotificationService.get_provider()
        
        if provider == 'twilio':
            return all([
                hasattr(settings, 'TWILIO_ACCOUNT_SID'),
                hasattr(settings, 'TWILIO_AUTH_TOKEN'),
                hasattr(settings, 'TWILIO_PHONE_NUMBER'),
            ])
        elif provider == 'africas_talking':
            return all([
                hasattr(settings, 'AFRICAS_TALKING_USERNAME'),
                hasattr(settings, 'AFRICAS_TALKING_API_KEY'),
            ])
        
        return False
    
    @staticmethod
    def send_sms_twilio(to_number, message):
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            msg = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            logger.info(f"Twilio SMS sent successfully to {to_number}, SID: {msg.sid}")
            return {'success': True, 'external_id': msg.sid}
        
        except Exception as e:
            logger.error(f"Twilio SMS failed to {to_number}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_sms_africas_talking(to_number, message):
        """Send SMS via Africa's Talking"""
        try:
            import africastalking
            
            # Initialize SDK
            africastalking.initialize(
                settings.AFRICAS_TALKING_USERNAME,
                settings.AFRICAS_TALKING_API_KEY
            )
            
            # Get SMS service
            sms = africastalking.SMS
            
            # Send message
            response = sms.send(message, [to_number])
            
            # Extract message ID from response
            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            if recipients and len(recipients) > 0:
                message_id = recipients[0].get('messageId', '')
                status = recipients[0].get('status', '')
                
                if 'Success' in status or 'Sent' in status:
                    logger.info(f"Africa's Talking SMS sent successfully to {to_number}, ID: {message_id}")
                    return {'success': True, 'external_id': message_id}
                else:
                    logger.error(f"Africa's Talking SMS failed to {to_number}: {status}")
                    return {'success': False, 'error': status}
            else:
                logger.error(f"Africa's Talking SMS failed to {to_number}: No recipients in response")
                return {'success': False, 'error': 'No recipients in response'}
        
        except Exception as e:
            logger.error(f"Africa's Talking SMS failed to {to_number}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_sms(user, notification_type, message):
        """
        Send SMS notification to user
        Checks preferences and logs result
        """
        if not user.phone_number:
            logger.warning(f"Cannot send SMS to {user.username}: No phone number")
            return False
        
        # Check if SMS is configured
        if not SMSNotificationService.is_configured():
            logger.warning("SMS service not configured, skipping SMS notification")
            return False
        
        # Check user preferences
        prefs = NotificationPreference.objects.filter(user=user).first()
        if prefs:
            channels = prefs.get_enabled_channels(notification_type)
            if 'sms' not in channels:
                logger.info(f"SMS disabled for {user.username} for {notification_type}")
                return False
        
        # Get provider and send
        provider = SMSNotificationService.get_provider()
        
        if provider == 'twilio':
            result = SMSNotificationService.send_sms_twilio(user.phone_number, message)
        elif provider == 'africas_talking':
            result = SMSNotificationService.send_sms_africas_talking(user.phone_number, message)
        else:
            logger.error(f"Unknown SMS provider: {provider}")
            return False
        
        # Log result
        log = NotificationLog.objects.create(
            user=user,
            notification_type=notification_type,
            channel='sms',
            recipient=user.phone_number,
            message=message,
            status='sent' if result['success'] else 'failed',
            error_message=result.get('error', ''),
            external_id=result.get('external_id', ''),
            sent_at=timezone.now() if result['success'] else None
        )
        
        return result['success']
    
    @staticmethod
    def send_appointment_reminder(appointment):
        """Send appointment reminder SMS"""
        if not appointment.user:
            logger.warning(f"Cannot send reminder for appointment {appointment.id}: No user")
            return False
        
        # Format message
        message = (
            f"🩸 Reminder: Blood donation appointment tomorrow "
            f"{appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.get_time_slot_display()} "
            f"at {appointment.location}. Thank you for saving lives! "
            f"- Blood Bank"
        )
        
        return SMSNotificationService.send_sms(
            appointment.user,
            'appointment_reminder',
            message
        )
    
    @staticmethod
    def send_urgent_blood_sms(donor, blood_type, urgency='high'):
        """Send urgent blood need SMS to donor"""
        if not donor.user:
            logger.warning(f"Cannot send SMS to donor {donor.id}: No user")
            return False
        
        # Format message based on urgency
        if urgency == 'critical':
            message = (
                f"🚨 CRITICAL: {blood_type} blood urgently needed! "
                f"Your donation can save a life TODAY. "
                f"Please contact us immediately: {getattr(settings, 'BLOOD_BANK_CONTACT', 'Blood Bank')}"
            )
        else:
            message = (
                f"🩸 Urgent: {blood_type} blood needed. "
                f"Can you donate? Your help saves lives. "
                f"Contact: {getattr(settings, 'BLOOD_BANK_CONTACT', 'Blood Bank')}"
            )
        
        return SMSNotificationService.send_sms(
            donor.user,
            'urgent_blood',
            message
        )
    
    @staticmethod
    def send_booking_confirmation_sms(appointment):
        """Send appointment booking confirmation SMS"""
        if not appointment.user:
            return False
        
        message = (
            f"✅ Appointment confirmed! "
            f"{appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.get_time_slot_display()} "
            f"at {appointment.location}. "
            f"Thank you for donating blood!"
        )
        
        return SMSNotificationService.send_sms(
            appointment.user,
            'booking_confirmation',
            message
        )
    
    @staticmethod
    def send_request_status_sms(blood_request, status):
        """Send blood request status update SMS"""
        message = (
            f"Blood Request Update: Your request for {blood_request.blood_type} "
            f"has been {status}. "
            f"Patient: {blood_request.patient_name}. "
            f"Check your email for details."
        )
        
        return SMSNotificationService.send_sms(
            blood_request.requester,
            'request_status',
            message
        )
    
    @staticmethod
    def send_bulk_sms(users, notification_type, message):
        """
        Send SMS to multiple users
        Returns count of successful sends
        """
        sent_count = 0
        
        for user in users:
            if SMSNotificationService.send_sms(user, notification_type, message):
                sent_count += 1
        
        logger.info(f"Bulk SMS: Sent {sent_count}/{len(users)} messages for {notification_type}")
        return sent_count
