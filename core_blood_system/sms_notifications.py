"""
SMS Notification System using Twilio
Configure Twilio credentials in settings.py to enable SMS
"""
from django.conf import settings


def send_sms(to_phone, message):
    """
    Send SMS using Twilio
    
    To enable SMS:
    1. Install twilio: pip install twilio
    2. Add to settings.py:
       TWILIO_ACCOUNT_SID = 'your_account_sid'
       TWILIO_AUTH_TOKEN = 'your_auth_token'
       TWILIO_PHONE_NUMBER = 'your_twilio_phone'
    """
    try:
        # Check if Twilio is configured
        if not hasattr(settings, 'TWILIO_ACCOUNT_SID'):
            print(f"SMS not sent (Twilio not configured): {message[:50]}...")
            return False
        
        from twilio.rest import Client
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        
        print(f"SMS sent successfully: {message.sid}")
        return True
        
    except ImportError:
        print("Twilio not installed. Run: pip install twilio")
        return False
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return False


def send_urgent_blood_request_sms(blood_request, donors):
    """
    Send SMS to matching donors for urgent blood requests
    """
    message = f"""
URGENT BLOOD REQUEST

Blood Type: {blood_request.blood_type}
Units Needed: {blood_request.units_needed}
Hospital: {blood_request.hospital_name}
Contact: {blood_request.contact_number}

Your donation can save a life!
    """.strip()
    
    sent_count = 0
    for donor in donors:
        if donor.phone_number:
            if send_sms(donor.phone_number, message):
                sent_count += 1
    
    return sent_count


def send_appointment_reminder_sms(appointment):
    """
    Send SMS reminder for upcoming appointment
    """
    message = f"""
APPOINTMENT REMINDER

Dear {appointment.donor.first_name},

Your blood donation appointment:
Date: {appointment.appointment_date.strftime('%b %d, %Y')}
Time: {appointment.get_time_slot_display()}
Location: {appointment.location}

Please arrive 10 minutes early.

Thank you for saving lives!
    """.strip()
    
    return send_sms(appointment.donor.phone_number, message)


def send_donation_thank_you_sms(donation):
    """
    Send thank you SMS after donation
    """
    message = f"""
Thank you, {donation.donor.first_name}!

Your donation of {donation.units_donated} unit(s) of {donation.blood_type} blood on {donation.donation_date.strftime('%b %d')} can save up to 3 lives!

You're a hero! 💪

- Blood Management System
    """.strip()
    
    return send_sms(donation.donor.phone_number, message)


def send_eligibility_notification_sms(donor, next_eligible_date):
    """
    Notify donor when they're eligible to donate again
    """
    message = f"""
Hi {donor.first_name}!

You're now eligible to donate blood again!

Next donation date: {next_eligible_date.strftime('%b %d, %Y')}

Schedule your appointment today and continue saving lives!

Blood Management System
    """.strip()
    
    return send_sms(donor.phone_number, message)


def send_low_stock_alert_sms(blood_type, admin_phones):
    """
    Alert administrators about low blood stock via SMS
    """
    message = f"""
⚠️ LOW STOCK ALERT

Blood Type: {blood_type}
Action required: Contact donors immediately

- Blood Management System
    """.strip()
    
    sent_count = 0
    for phone in admin_phones:
        if send_sms(phone, message):
            sent_count += 1
    
    return sent_count


# Configuration instructions
SMS_SETUP_INSTRUCTIONS = """
To enable SMS notifications:

1. Install Twilio SDK:
   pip install twilio

2. Sign up for Twilio account:
   https://www.twilio.com/try-twilio

3. Add to backend/settings.py:
   
   # Twilio Configuration
   TWILIO_ACCOUNT_SID = 'your_account_sid_here'
   TWILIO_AUTH_TOKEN = 'your_auth_token_here'
   TWILIO_PHONE_NUMBER = '+1234567890'  # Your Twilio phone number

4. Test SMS:
   from core_blood_system.sms_notifications import send_sms
   send_sms('+1234567890', 'Test message')

Note: Twilio trial accounts can only send to verified phone numbers.
"""
