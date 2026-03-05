# SMS Notification Setup Guide

## Overview

The Blood Management System now supports SMS notifications via two providers:
1. **Twilio** - Global SMS service (recommended for international use)
2. **Africa's Talking** - African SMS service (recommended for Kenya and Africa)

SMS notifications are sent for:
- Urgent blood need alerts
- Appointment reminders (24 hours before)
- Appointment booking confirmations
- Blood request status updates

## Features

- Multi-provider support (Twilio or Africa's Talking)
- User preference management (users can opt-in/out)
- Automatic notification logging
- Graceful fallback (email-only if SMS not configured)
- Error handling and retry logic

---

## Setup Instructions

### Option 1: Africa's Talking (Recommended for Kenya)

#### Step 1: Create Africa's Talking Account

1. Visit https://africastalking.com/
2. Sign up for an account
3. Verify your account
4. Go to Dashboard → Settings → API Key
5. Copy your **Username** and **API Key**

#### Step 2: Add Credits

1. Go to Dashboard → Billing
2. Add credits to your account (minimum $5)
3. SMS costs approximately $0.01 per message in Kenya

#### Step 3: Configure Django Settings

Add to `backend/settings.py` or `backend/production_settings.py`:

```python
# SMS Configuration
SMS_PROVIDER = 'africas_talking'
AFRICAS_TALKING_USERNAME = 'your_username'  # From dashboard
AFRICAS_TALKING_API_KEY = 'your_api_key'    # From dashboard
```

Or use environment variables (recommended for production):

```bash
export SMS_PROVIDER=africas_talking
export AFRICAS_TALKING_USERNAME=your_username
export AFRICAS_TALKING_API_KEY=your_api_key
```

#### Step 4: Install Python Package

```bash
pip install africastalking
```

#### Step 5: Test SMS

```python
python manage.py shell

from core_blood_system.sms_notifications import SMSNotificationService
from core_blood_system.models import CustomUser

# Get a test user
user = CustomUser.objects.first()

# Send test SMS
result = SMSNotificationService.send_sms(
    user, 
    'appointment_reminder', 
    'Test SMS from Blood Bank System'
)

print(f"SMS sent: {result}")
```

---

### Option 2: Twilio (Global)

#### Step 1: Create Twilio Account

1. Visit https://www.twilio.com/
2. Sign up for a free trial account
3. Verify your phone number
4. Get your **Account SID** and **Auth Token** from the dashboard
5. Get a Twilio phone number

#### Step 2: Configure Django Settings

Add to `backend/settings.py` or `backend/production_settings.py`:

```python
# SMS Configuration
SMS_PROVIDER = 'twilio'
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'  # Your Twilio number
```

Or use environment variables:

```bash
export SMS_PROVIDER=twilio
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
export TWILIO_PHONE_NUMBER=+1234567890
```

#### Step 3: Install Python Package

```bash
pip install twilio
```

#### Step 4: Test SMS

```python
python manage.py shell

from core_blood_system.sms_notifications import SMSNotificationService
from core_blood_system.models import CustomUser

user = CustomUser.objects.first()

result = SMSNotificationService.send_sms(
    user, 
    'appointment_reminder', 
    'Test SMS from Blood Bank System'
)

print(f"SMS sent: {result}")
```

---

## PythonAnywhere Deployment

### Step 1: Update Requirements

Add to `requirements.txt`:

```
twilio==8.10.0
africastalking==1.2.7
```

### Step 2: Install Packages

In PythonAnywhere console:

```bash
cd /home/kibeterick/blood_management_fullstack
pip install --user twilio africastalking
```

### Step 3: Configure Environment Variables

Option A: Add to `backend/production_settings.py`:

```python
# SMS Configuration
SMS_PROVIDER = 'africas_talking'  # or 'twilio'
AFRICAS_TALKING_USERNAME = 'your_username'
AFRICAS_TALKING_API_KEY = 'your_api_key'
```

Option B: Use PythonAnywhere environment variables:
1. Go to Web tab
2. Scroll to "Environment variables"
3. Add:
   - `SMS_PROVIDER` = `africas_talking`
   - `AFRICAS_TALKING_USERNAME` = `your_username`
   - `AFRICAS_TALKING_API_KEY` = `your_api_key`

### Step 4: Reload Web App

```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

Or click "Reload" button in PythonAnywhere Web tab.

---

## User Notification Preferences

Users can control which notifications they receive via SMS:

### Default Settings

When a user registers, default preferences are:
- Email: Enabled for all notifications
- SMS: Disabled by default (to avoid unexpected charges)

### Enabling SMS Notifications

Users can enable SMS notifications from their dashboard:
1. Log in to account
2. Go to "Notification Preferences"
3. Enable SMS for desired notification types:
   - Urgent blood needs
   - Appointment reminders
   - Booking confirmations
   - Request status updates

### Admin Override

Admins can send urgent SMS notifications regardless of user preferences for critical situations.

---

## Cost Estimates

### Africa's Talking (Kenya)

- SMS to Kenya: ~$0.01 per message
- 1000 SMS = ~$10
- Bulk discounts available

### Twilio (Global)

- SMS to Kenya: ~$0.05 per message
- SMS to USA: ~$0.0075 per message
- 1000 SMS = ~$7.50 - $50 depending on country

### Recommendations

- **Kenya/Africa**: Use Africa's Talking (cheaper, better delivery)
- **Global**: Use Twilio (wider coverage)
- **Budget**: Start with email-only, add SMS for critical alerts only

---

## Notification Logging

All SMS notifications are logged in the `NotificationLog` model:

### View Logs (Admin)

```python
python manage.py shell

from core_blood_system.models import NotificationLog

# Recent SMS logs
logs = NotificationLog.objects.filter(channel='sms').order_by('-created_at')[:10]

for log in logs:
    print(f"{log.created_at}: {log.notification_type} to {log.recipient} - {log.status}")
```

### Check Failed SMS

```python
failed = NotificationLog.objects.filter(channel='sms', status='failed')

for log in failed:
    print(f"Failed: {log.recipient} - {log.error_message}")
```

---

## Troubleshooting

### Issue: SMS not sending

**Check 1: Is SMS configured?**
```python
from core_blood_system.sms_notifications import SMSNotificationService
print(SMSNotificationService.is_configured())  # Should be True
```

**Check 2: Check provider**
```python
print(SMSNotificationService.get_provider())  # Should be 'twilio' or 'africas_talking'
```

**Check 3: Check user phone number**
```python
from core_blood_system.models import CustomUser
user = CustomUser.objects.get(username='testuser')
print(user.phone_number)  # Should be in format: +254712345678
```

**Check 4: Check notification logs**
```python
from core_blood_system.models import NotificationLog
logs = NotificationLog.objects.filter(channel='sms', status='failed').order_by('-created_at')[:5]
for log in logs:
    print(f"Error: {log.error_message}")
```

### Issue: "Invalid phone number"

Phone numbers must be in international format:
- ✅ Correct: `+254712345678` (Kenya)
- ✅ Correct: `+1234567890` (USA)
- ❌ Wrong: `0712345678`
- ❌ Wrong: `712345678`

### Issue: "Insufficient credits" (Africa's Talking)

1. Log in to Africa's Talking dashboard
2. Go to Billing
3. Add more credits
4. Retry sending SMS

### Issue: "Authentication failed" (Twilio)

1. Verify Account SID and Auth Token are correct
2. Check if trial account has expired
3. Verify phone number is verified (for trial accounts)

---

## Best Practices

### 1. Phone Number Validation

Always store phone numbers in international format:

```python
# Good
user.phone_number = '+254712345678'

# Bad
user.phone_number = '0712345678'
```

### 2. Message Length

Keep SMS messages under 160 characters to avoid multi-part messages:

```python
# Good (short and clear)
message = "Appointment tomorrow 10AM at City Hospital. Thank you!"

# Bad (too long, will be split into multiple SMS)
message = "Your blood donation appointment is scheduled for tomorrow at 10:00 AM at City Hospital located at 123 Main Street. Please arrive 15 minutes early and bring your ID. Thank you for saving lives!"
```

### 3. Rate Limiting

Avoid sending too many SMS at once:

```python
# Good (batch with delays)
import time
for user in users:
    SMSNotificationService.send_sms(user, 'urgent_blood', message)
    time.sleep(0.5)  # 500ms delay between messages

# Bad (all at once, may hit rate limits)
for user in users:
    SMSNotificationService.send_sms(user, 'urgent_blood', message)
```

### 4. Cost Management

- Enable SMS only for critical notifications
- Use email for non-urgent communications
- Set up billing alerts in provider dashboard
- Monitor usage regularly

### 5. User Consent

- Always get user consent before sending SMS
- Provide easy opt-out mechanism
- Respect user preferences
- Include unsubscribe instructions

---

## Testing

### Test SMS Sending

```bash
python manage.py shell
```

```python
from core_blood_system.sms_notifications import SMSNotificationService
from core_blood_system.models import CustomUser, Donor, DonationAppointment
from datetime import date, timedelta

# Test 1: Simple SMS
user = CustomUser.objects.first()
result = SMSNotificationService.send_sms(user, 'appointment_reminder', 'Test message')
print(f"Test 1: {result}")

# Test 2: Appointment reminder
appointment = DonationAppointment.objects.first()
result = SMSNotificationService.send_appointment_reminder(appointment)
print(f"Test 2: {result}")

# Test 3: Urgent blood SMS
donor = Donor.objects.first()
result = SMSNotificationService.send_urgent_blood_sms(donor, 'O+', 'critical')
print(f"Test 3: {result}")
```

---

## Security Considerations

### 1. Protect API Keys

Never commit API keys to version control:

```python
# Good (use environment variables)
SMS_PROVIDER = os.environ.get('SMS_PROVIDER')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

# Bad (hardcoded)
TWILIO_AUTH_TOKEN = 'abc123xyz'
```

### 2. Validate Phone Numbers

Always validate phone numbers before sending:

```python
import re

def is_valid_phone(phone):
    # International format: +[country code][number]
    pattern = r'^\+[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None
```

### 3. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from django.core.cache import cache

def can_send_sms(user):
    key = f'sms_limit_{user.id}'
    count = cache.get(key, 0)
    
    if count >= 10:  # Max 10 SMS per hour
        return False
    
    cache.set(key, count + 1, 3600)  # 1 hour
    return True
```

---

## Monitoring

### Dashboard Metrics

Track these metrics:
- Total SMS sent (daily/weekly/monthly)
- Success rate
- Failed SMS count
- Cost per SMS
- User opt-in rate

### Query Examples

```python
from core_blood_system.models import NotificationLog
from django.db.models import Count
from datetime import datetime, timedelta

# SMS sent today
today = datetime.now().date()
sms_today = NotificationLog.objects.filter(
    channel='sms',
    created_at__date=today
).count()

# Success rate
total = NotificationLog.objects.filter(channel='sms').count()
successful = NotificationLog.objects.filter(channel='sms', status='sent').count()
success_rate = (successful / total * 100) if total > 0 else 0

print(f"SMS today: {sms_today}")
print(f"Success rate: {success_rate:.1f}%")
```

---

## Support

### Africa's Talking Support
- Email: support@africastalking.com
- Docs: https://developers.africastalking.com/
- Phone: +254 20 524 2223

### Twilio Support
- Email: help@twilio.com
- Docs: https://www.twilio.com/docs/
- Phone: +1 (415) 390-2337

---

## Summary

SMS notifications are now fully integrated into the Blood Management System. The system supports both Twilio and Africa's Talking, with automatic fallback to email if SMS is not configured. All notifications are logged for tracking and debugging.

**Next Steps:**
1. Choose SMS provider (Africa's Talking for Kenya, Twilio for global)
2. Create account and get API credentials
3. Configure Django settings
4. Install required packages
5. Test SMS sending
6. Deploy to production
7. Monitor usage and costs

**Status:** ✅ Task 7 Complete - SMS Notification Service Implemented
