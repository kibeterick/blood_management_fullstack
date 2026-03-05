# Scheduled Tasks Deployment Guide

This guide explains how to deploy the scheduled notification tasks for the Blood Management System. Two approaches are provided:

1. **Celery with Redis** (for production servers with full control)
2. **Django Management Commands** (for PythonAnywhere and similar platforms)

## Overview

The system includes three scheduled tasks:

1. **Send Appointment Reminders** - Runs daily at 9:00 AM
   - Sends email and SMS reminders for appointments 24 hours away
   - Marks appointments as reminder_sent

2. **Mark Expired Blood Units** - Runs daily at midnight
   - Marks blood units past their expiration date as expired
   - Updates inventory counts

3. **Check Low Stock** - Runs daily at 8:00 AM
   - Checks inventory thresholds
   - Sends alerts to admins for low/critical stock
   - Respects 24-hour notification limit

---

## Option 1: Celery with Redis (Production Servers)

### Prerequisites

```bash
pip install celery redis django-celery-beat
```

### Configuration

The Celery configuration is already set up in:
- `core_blood_system/celery.py` - Celery app and beat schedule
- `core_blood_system/tasks.py` - Task implementations
- `backend/settings.py` - Celery settings

### Environment Variables

Add to your `.env` file or environment:

```bash
# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# SMS Configuration (optional)
SMS_PROVIDER=twilio  # or 'africas_talking'
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Blood Bank Contact
BLOOD_BANK_CONTACT=+1234567890
```

### Running Celery

**Terminal 1 - Celery Worker:**
```bash
celery -A core_blood_system worker --loglevel=info
```

**Terminal 2 - Celery Beat (Scheduler):**
```bash
celery -A core_blood_system beat --loglevel=info
```

**Combined (for development):**
```bash
celery -A core_blood_system worker --beat --loglevel=info
```

### Systemd Service (Linux Production)

Create `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker for Blood Management System
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/blood_management_fullstack
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A core_blood_system worker --detach --loglevel=info
ExecStop=/path/to/venv/bin/celery -A core_blood_system control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/celery-beat.service`:

```ini
[Unit]
Description=Celery Beat for Blood Management System
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/blood_management_fullstack
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A core_blood_system beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
```

---

## Option 2: Django Management Commands (PythonAnywhere)

### Why This Approach?

PythonAnywhere free/basic accounts don't support:
- Long-running background processes (Celery workers)
- Redis or other message brokers
- WebSocket connections

Instead, use PythonAnywhere's **Scheduled Tasks** feature with Django management commands.

### Available Commands

Three management commands are provided:

1. `python manage.py send_appointment_reminders`
2. `python manage.py mark_expired_units`
3. `python manage.py check_low_stock`

### Testing Commands Locally

```bash
# Test appointment reminders
python manage.py send_appointment_reminders

# Test marking expired units
python manage.py mark_expired_units

# Test low stock alerts
python manage.py check_low_stock
```

### PythonAnywhere Setup

#### Step 1: Upload Code

1. Push your code to GitHub
2. Pull on PythonAnywhere:
   ```bash
   cd ~/blood_management_fullstack
   git pull origin main
   ```

#### Step 2: Install Dependencies

```bash
cd ~/blood_management_fullstack
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables

Edit `~/.bashrc` or use PythonAnywhere's environment variables:

```bash
export SMS_PROVIDER=twilio
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
export TWILIO_PHONE_NUMBER=+1234567890
export BLOOD_BANK_CONTACT=+1234567890
```

#### Step 4: Set Up Scheduled Tasks

Go to PythonAnywhere Dashboard → Tasks tab

**Task 1: Send Appointment Reminders (Daily at 9:00 AM)**
```bash
cd /home/yourusername/blood_management_fullstack && source venv/bin/activate && python manage.py send_appointment_reminders
```
Schedule: `09:00` (daily)

**Task 2: Mark Expired Units (Daily at 00:00)**
```bash
cd /home/yourusername/blood_management_fullstack && source venv/bin/activate && python manage.py mark_expired_units
```
Schedule: `00:00` (daily)

**Task 3: Check Low Stock (Daily at 8:00 AM)**
```bash
cd /home/yourusername/blood_management_fullstack && source venv/bin/activate && python manage.py check_low_stock
```
Schedule: `08:00` (daily)

#### Step 5: Reload Web App

After setting up tasks, reload your web app from the Web tab.

### Monitoring

Check task execution logs in PythonAnywhere:
- Go to Tasks tab
- Click on each task to see execution history
- Check for errors or success messages

---

## SMS Configuration

### Twilio Setup

1. Sign up at https://www.twilio.com/
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Set environment variables:
   ```bash
   SMS_PROVIDER=twilio
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Africa's Talking Setup

1. Sign up at https://africastalking.com/
2. Get your API Key
3. Set environment variables:
   ```bash
   SMS_PROVIDER=africas_talking
   AFRICAS_TALKING_USERNAME=your_username
   AFRICAS_TALKING_API_KEY=your_api_key
   ```

### Disabling SMS

If you don't want SMS notifications:
- Don't set `SMS_PROVIDER` environment variable
- Email notifications will still work
- SMS methods will gracefully skip

---

## Email Configuration

Ensure Django email settings are configured in `backend/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@bloodbank.com'
```

For PythonAnywhere, you can use:
- Gmail SMTP (with app password)
- SendGrid
- Mailgun
- PythonAnywhere's built-in email

---

## Troubleshooting

### Celery Issues

**Problem:** Tasks not running
```bash
# Check Celery worker status
celery -A core_blood_system inspect active

# Check scheduled tasks
celery -A core_blood_system inspect scheduled

# Restart workers
celery -A core_blood_system control shutdown
celery -A core_blood_system worker --beat --loglevel=info
```

**Problem:** Redis connection error
```bash
# Check Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis
```

### PythonAnywhere Issues

**Problem:** Command not found
- Ensure you're using the full path to Python in your virtual environment
- Check the working directory is correct

**Problem:** Import errors
- Verify all dependencies are installed in the virtual environment
- Check `requirements.txt` is up to date

**Problem:** Tasks not executing
- Check the Tasks tab for error messages
- Verify the schedule time is correct (use 24-hour format)
- Ensure the web app has been reloaded

### Email Issues

**Problem:** Emails not sending
- Check Django email settings
- Verify SMTP credentials
- Check spam folder
- Review NotificationLog model for error messages

**Problem:** SMS not sending
- Verify SMS_PROVIDER is set correctly
- Check provider credentials
- Ensure phone numbers are in E.164 format (+1234567890)
- Review NotificationLog model for error messages

---

## Testing

### Manual Testing

```bash
# Create a test appointment for tomorrow
python manage.py shell
>>> from datetime import date, timedelta
>>> from core_blood_system.models import DonationAppointment, Donor
>>> donor = Donor.objects.first()
>>> appointment = DonationAppointment.objects.create(
...     donor=donor,
...     user=donor.user,
...     appointment_date=date.today() + timedelta(days=1),
...     time_slot='10:00',
...     location='Main Blood Bank',
...     status='scheduled',
...     reminder_sent=False
... )
>>> exit()

# Run the reminder task
python manage.py send_appointment_reminders

# Check NotificationLog
python manage.py shell
>>> from core_blood_system.models import NotificationLog
>>> NotificationLog.objects.latest('created_at')
```

### Automated Testing

Create test cases in `core_blood_system/tests.py`:

```python
from django.test import TestCase
from django.core.management import call_command
from datetime import date, timedelta
from .models import DonationAppointment, BloodUnit

class ScheduledTasksTestCase(TestCase):
    def test_send_appointment_reminders(self):
        # Create test appointment
        # Run command
        call_command('send_appointment_reminders')
        # Assert reminder was sent
    
    def test_mark_expired_units(self):
        # Create expired unit
        # Run command
        call_command('mark_expired_units')
        # Assert unit is marked expired
```

---

## Monitoring and Logs

### Celery Logs

```bash
# View worker logs
tail -f /var/log/celery/worker.log

# View beat logs
tail -f /var/log/celery/beat.log
```

### Django Logs

Check `NotificationLog` model for all notification attempts:

```python
from core_blood_system.models import NotificationLog

# Recent notifications
NotificationLog.objects.order_by('-created_at')[:10]

# Failed notifications
NotificationLog.objects.filter(status='failed')

# Notifications by type
NotificationLog.objects.filter(notification_type='appointment_reminder')
```

### PythonAnywhere Logs

- Task execution logs: Tasks tab → Click on task
- Error logs: Files tab → `/var/log/`
- Web app logs: Web tab → Log files section

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Email backend tested
- [ ] SMS provider configured (if using)
- [ ] Scheduled tasks set up (Celery or PythonAnywhere)
- [ ] Test notifications sent successfully
- [ ] NotificationLog entries created
- [ ] Monitoring set up
- [ ] Error alerting configured
- [ ] Documentation updated

---

## Support

For issues or questions:
1. Check NotificationLog for error messages
2. Review Django logs
3. Test commands manually
4. Verify environment variables
5. Check email/SMS provider status

---

## Summary

**For Production Servers:** Use Celery with Redis for robust, scalable task scheduling.

**For PythonAnywhere:** Use Django management commands with PythonAnywhere's scheduled tasks feature.

Both approaches provide the same functionality - choose based on your hosting environment.
