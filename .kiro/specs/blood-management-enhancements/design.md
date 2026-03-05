# Design Document: Blood Management Enhancements

## Overview

This design document specifies the technical implementation for three priority enhancements to the Blood Management System:

1. **Blood Bank Inventory Management**: Real-time tracking of blood units with expiration management, low stock alerts, and visual dashboards
2. **SMS/Email Notifications**: Multi-channel notification system for urgent blood needs, appointment reminders, and status updates
3. **Donor Eligibility Checker**: Pre-screening questionnaire and validation system to ensure donor safety and compliance

These features integrate with the existing Django-based system deployed on PythonAnywhere, maintaining compatibility with current models (CustomUser, Donor, BloodRequest, BloodDonation, BloodInventory, DonationAppointment) and following established design patterns.

### Design Goals

- Seamless integration with existing donor management and appointment systems
- Real-time inventory tracking with automated alerting
- Multi-channel notification delivery (email and SMS)
- Comprehensive donor eligibility validation
- Mobile-responsive UI following the existing red/blood theme
- PythonAnywhere deployment compatibility
- Minimal performance impact on existing functionality

### Technology Stack

- **Backend**: Django 4.x with existing models and views
- **Database**: MySQL (existing PythonAnywhere setup)
- **Frontend**: Bootstrap 5, Chart.js for visualizations
- **Email**: Django email backend (PythonAnywhere SMTP)
- **SMS**: Twilio or Africa's Talking API integration
- **Task Queue**: Celery with Redis for scheduled notifications
- **Charts**: Chart.js for inventory visualization


## Architecture

### System Architecture

The enhancements follow a layered architecture pattern consistent with the existing Django application:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  (Templates, Forms, Chart.js Visualizations)                │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Inventory   │  │ Notification │  │  Eligibility │     │
│  │   Manager    │  │   Service    │  │   Checker    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  BloodUnit   │  │ Notification │  │    Donor     │     │
│  │ BloodInv...  │  │ Preference   │  │ Eligibility  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Django    │  │    Twilio    │  │   Celery     │     │
│  │    Email     │  │  Africa's    │  │   Redis      │     │
│  │              │  │   Talking    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**Inventory Management Flow:**
```
Donation Approved → Update BloodUnit → Update BloodInventory → 
Check Threshold → Trigger Alert (if low) → Send Notification
```

**Notification Flow:**
```
Event Trigger → Check User Preferences → Select Channel(s) → 
Queue Notification → Send via Email/SMS → Log Result
```

**Eligibility Check Flow:**
```
User Initiates Booking → Present Questionnaire → Collect Responses → 
Validate Criteria → Calculate Eligibility → Store Result → 
Enable/Disable Booking
```


## Components and Interfaces

### Feature 1: Blood Bank Inventory Management

#### Database Models

**BloodUnit Model** (New)
```python
class BloodUnit(models.Model):
    """Individual blood unit tracking with expiration management"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('discarded', 'Discarded'),
    ]
    
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    donation = models.ForeignKey(BloodDonation, on_delete=models.SET_NULL, 
                                null=True, blank=True, related_name='blood_units')
    donation_date = models.DateField()
    expiration_date = models.DateField()  # Typically 42 days from donation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    unit_number = models.CharField(max_length=50, unique=True)  # Unique identifier
    volume_ml = models.IntegerField(default=450)  # Standard unit volume
    storage_location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['expiration_date', 'donation_date']
        indexes = [
            models.Index(fields=['blood_type', 'status']),
            models.Index(fields=['expiration_date']),
        ]
    
    def is_expiring_soon(self):
        """Check if unit expires within 7 days"""
        from datetime import date, timedelta
        return (self.expiration_date - date.today()).days <= 7
    
    def is_expired(self):
        """Check if unit has expired"""
        from datetime import date
        return self.expiration_date < date.today()
```

**BloodInventory Model** (Enhanced - already exists)
```python
# Existing model with added fields:
class BloodInventory(models.Model):
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, unique=True)
    units_available = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    minimum_threshold = models.IntegerField(default=5)
    # New fields:
    critical_threshold = models.IntegerField(default=2)  # Critical level
    optimal_level = models.IntegerField(default=20)  # Target stock level
    alert_sent_at = models.DateTimeField(null=True, blank=True)  # Last alert timestamp
    
    def get_status(self):
        """Return stock status: critical, low, adequate, optimal"""
        if self.units_available <= self.critical_threshold:
            return 'critical'
        elif self.units_available <= self.minimum_threshold:
            return 'low'
        elif self.units_available >= self.optimal_level:
            return 'optimal'
        return 'adequate'
```

#### Views and URL Patterns

**Inventory Dashboard View**
```python
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def inventory_dashboard(request):
    """Main inventory dashboard with real-time data and charts"""
    inventory = BloodInventory.objects.all()
    
    # Get expiring units (within 7 days)
    from datetime import date, timedelta
    expiring_soon = BloodUnit.objects.filter(
        status='available',
        expiration_date__lte=date.today() + timedelta(days=7)
    ).order_by('expiration_date')
    
    # Get expired units
    expired_units = BloodUnit.objects.filter(
        status='available',
        expiration_date__lt=date.today()
    )
    
    # Prepare chart data
    chart_data = {
        'labels': [inv.blood_type for inv in inventory],
        'quantities': [inv.units_available for inv in inventory],
        'thresholds': [inv.minimum_threshold for inv in inventory],
        'statuses': [inv.get_status() for inv in inventory],
    }
    
    context = {
        'inventory': inventory,
        'expiring_soon': expiring_soon,
        'expired_units': expired_units,
        'chart_data': chart_data,
    }
    return render(request, 'inventory/dashboard.html', context)
```

**Add/Update Stock View**
```python
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def add_blood_unit(request):
    """Add new blood unit to inventory"""
    if request.method == 'POST':
        form = BloodUnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            
            # Update inventory count
            inventory, created = BloodInventory.objects.get_or_create(
                blood_type=unit.blood_type
            )
            inventory.units_available = BloodUnit.objects.filter(
                blood_type=unit.blood_type,
                status='available'
            ).count()
            inventory.save()
            
            messages.success(request, f'Blood unit {unit.unit_number} added successfully')
            return redirect('inventory_dashboard')
    else:
        form = BloodUnitForm()
    
    return render(request, 'inventory/add_unit.html', {'form': form})
```

**Expiration Management View**
```python
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def expiration_list(request):
    """View all units sorted by expiration date"""
    from datetime import date, timedelta
    
    units = BloodUnit.objects.filter(status='available').order_by('expiration_date')
    
    # Categorize units
    expired = units.filter(expiration_date__lt=date.today())
    expiring_soon = units.filter(
        expiration_date__gte=date.today(),
        expiration_date__lte=date.today() + timedelta(days=7)
    )
    good = units.filter(expiration_date__gt=date.today() + timedelta(days=7))
    
    context = {
        'expired': expired,
        'expiring_soon': expiring_soon,
        'good': good,
    }
    return render(request, 'inventory/expiration_list.html', context)
```

**API Endpoint for Real-Time Updates**
```python
@login_required
def inventory_api(request):
    """JSON API for real-time inventory data"""
    inventory = BloodInventory.objects.all()
    data = [{
        'blood_type': inv.blood_type,
        'units_available': inv.units_available,
        'status': inv.get_status(),
        'threshold': inv.minimum_threshold,
        'last_updated': inv.last_updated.isoformat(),
    } for inv in inventory]
    
    return JsonResponse({'inventory': data})
```

#### Forms

**BloodUnitForm**
```python
class BloodUnitForm(forms.ModelForm):
    class Meta:
        model = BloodUnit
        fields = ['blood_type', 'donation', 'donation_date', 'expiration_date', 
                  'unit_number', 'volume_ml', 'storage_location', 'notes']
        widgets = {
            'donation_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-calculate expiration date (42 days from donation)
        if not self.instance.pk:
            from datetime import timedelta
            if self.initial.get('donation_date'):
                self.initial['expiration_date'] = (
                    self.initial['donation_date'] + timedelta(days=42)
                )
```

**InventoryThresholdForm**
```python
class InventoryThresholdForm(forms.ModelForm):
    class Meta:
        model = BloodInventory
        fields = ['minimum_threshold', 'critical_threshold', 'optimal_level']
        widgets = {
            'minimum_threshold': forms.NumberInput(attrs={'min': 1}),
            'critical_threshold': forms.NumberInput(attrs={'min': 1}),
            'optimal_level': forms.NumberInput(attrs={'min': 1}),
        }
```

#### Utility Functions

**Inventory Manager**
```python
class InventoryManager:
    """Centralized inventory management logic"""
    
    @staticmethod
    def update_inventory_from_donation(donation):
        """Update inventory when donation is approved"""
        if donation.status == 'approved':
            # Create blood unit
            from datetime import timedelta
            unit = BloodUnit.objects.create(
                blood_type=donation.blood_type,
                donation=donation,
                donation_date=donation.donation_date,
                expiration_date=donation.donation_date + timedelta(days=42),
                unit_number=f"BU-{donation.id}-{timezone.now().timestamp()}",
                volume_ml=450 * donation.units_donated,
            )
            
            # Update inventory count
            inventory, created = BloodInventory.objects.get_or_create(
                blood_type=donation.blood_type
            )
            inventory.units_available = BloodUnit.objects.filter(
                blood_type=donation.blood_type,
                status='available'
            ).count()
            inventory.save()
            
            # Check for low stock alert
            if inventory.is_low_stock():
                from .notifications import send_low_stock_alert
                send_low_stock_alert(inventory)
            
            return unit
        return None
    
    @staticmethod
    def mark_expired_units():
        """Mark expired units (run as scheduled task)"""
        from datetime import date
        expired_count = BloodUnit.objects.filter(
            status='available',
            expiration_date__lt=date.today()
        ).update(status='expired')
        
        # Update inventory counts
        if expired_count > 0:
            for blood_type in BLOOD_TYPE_CHOICES:
                inventory = BloodInventory.objects.filter(
                    blood_type=blood_type[0]
                ).first()
                if inventory:
                    inventory.units_available = BloodUnit.objects.filter(
                        blood_type=blood_type[0],
                        status='available'
                    ).count()
                    inventory.save()
        
        return expired_count
```


### Feature 2: SMS/Email Notifications

#### Database Models

**NotificationPreference Model** (New)
```python
class NotificationPreference(models.Model):
    """User notification preferences for channels and types"""
    NOTIFICATION_TYPE_CHOICES = [
        ('urgent_blood', 'Urgent Blood Need'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('booking_confirmation', 'Booking Confirmation'),
        ('request_status', 'Request Status Update'),
        ('low_stock', 'Low Stock Alert'),
        ('donation_approved', 'Donation Approved'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, 
                               related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    
    # Individual notification type preferences
    urgent_blood_email = models.BooleanField(default=True)
    urgent_blood_sms = models.BooleanField(default=False)
    appointment_reminder_email = models.BooleanField(default=True)
    appointment_reminder_sms = models.BooleanField(default=True)
    booking_confirmation_email = models.BooleanField(default=True)
    booking_confirmation_sms = models.BooleanField(default=False)
    request_status_email = models.BooleanField(default=True)
    request_status_sms = models.BooleanField(default=False)
    low_stock_email = models.BooleanField(default=True)
    low_stock_sms = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Preferences"
    
    def get_enabled_channels(self, notification_type):
        """Get enabled channels for a specific notification type"""
        channels = []
        if getattr(self, f'{notification_type}_email', False):
            channels.append('email')
        if getattr(self, f'{notification_type}_sms', False):
            channels.append('sms')
        return channels
```

**NotificationLog Model** (New)
```python
class NotificationLog(models.Model):
    """Log of all sent notifications for tracking and debugging"""
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                            related_name='notification_logs')
    notification_type = models.CharField(max_length=50)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=200)  # Email or phone number
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # External service tracking
    external_id = models.CharField(max_length=100, blank=True)  # Twilio SID, etc.
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type} via {self.channel}"
```

#### Notification Service

**Email Notification Service**
```python
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

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
                'contact_phone': settings.BLOOD_BANK_CONTACT,
            }
            
            html_message = render_to_string('notifications/urgent_blood_email.html', context)
            plain_message = render_to_string('notifications/urgent_blood_email.txt', context)
            
            try:
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
        
        return sent_count
    
    @staticmethod
    def send_appointment_confirmation(appointment):
        """Send appointment booking confirmation with calendar attachment"""
        if not appointment.user:
            return False
        
        prefs = NotificationPreference.objects.filter(user=appointment.user).first()
        if prefs and not prefs.booking_confirmation_email:
            return False
        
        subject = f"Appointment Confirmed - {appointment.appointment_date}"
        
        context = {
            'appointment': appointment,
            'donor': appointment.donor,
        }
        
        html_message = render_to_string('notifications/appointment_confirmation.html', context)
        plain_message = render_to_string('notifications/appointment_confirmation.txt', context)
        
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[appointment.donor.email]
            )
            msg.attach_alternative(html_message, "text/html")
            
            # Attach ICS calendar file
            ics_content = generate_ics_file(appointment)
            msg.attach('appointment.ics', ics_content, 'text/calendar')
            
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
            return True
        except Exception as e:
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
        
        html_message = render_to_string('notifications/request_status_email.html', context)
        plain_message = render_to_string('notifications/request_status_email.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[blood_request.requester.email],
                html_message=html_message,
                fail_silently=False
            )
            
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
            return True
        except Exception as e:
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
```

**SMS Notification Service**
```python
from django.conf import settings
import requests

class SMSNotificationService:
    """Handle SMS notifications via Twilio or Africa's Talking"""
    
    @staticmethod
    def get_provider():
        """Get configured SMS provider"""
        return getattr(settings, 'SMS_PROVIDER', None)
    
    @staticmethod
    def send_sms_twilio(to_number, message):
        """Send SMS via Twilio"""
        from twilio.rest import Client
        
        try:
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            msg = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            return {'success': True, 'external_id': msg.sid}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_sms_africas_talking(to_number, message):
        """Send SMS via Africa's Talking"""
        import africastalking
        
        try:
            africastalking.initialize(
                settings.AFRICAS_TALKING_USERNAME,
                settings.AFRICAS_TALKING_API_KEY
            )
            
            sms = africastalking.SMS
            response = sms.send(message, [to_number])
            
            return {'success': True, 'external_id': response['SMSMessageData']['Recipients'][0]['messageId']}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_sms(user, notification_type, message):
        """Send SMS notification to user"""
        if not user.phone_number:
            return False
        
        # Check preferences
        prefs = NotificationPreference.objects.filter(user=user).first()
        if prefs:
            channels = prefs.get_enabled_channels(notification_type)
            if 'sms' not in channels:
                return False
        
        provider = SMSNotificationService.get_provider()
        
        if provider == 'twilio':
            result = SMSNotificationService.send_sms_twilio(user.phone_number, message)
        elif provider == 'africas_talking':
            result = SMSNotificationService.send_sms_africas_talking(user.phone_number, message)
        else:
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
            return False
        
        message = (
            f"Reminder: Blood donation appointment tomorrow "
            f"{appointment.appointment_date} at {appointment.get_time_slot_display()} "
            f"at {appointment.location}. Thank you for saving lives!"
        )
        
        return SMSNotificationService.send_sms(
            appointment.user,
            'appointment_reminder',
            message
        )
```


#### Celery Tasks for Scheduled Notifications

**Task Configuration**
```python
# celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery('blood_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'core_blood_system.tasks.send_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'mark-expired-blood-units': {
        'task': 'core_blood_system.tasks.mark_expired_units',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

**Celery Tasks**
```python
# tasks.py
from celery import shared_task
from datetime import date, timedelta
from .models import DonationAppointment, BloodUnit
from .notifications import EmailNotificationService, SMSNotificationService

@shared_task
def send_appointment_reminders():
    """Send reminders for appointments 24 hours away"""
    tomorrow = date.today() + timedelta(days=1)
    
    appointments = DonationAppointment.objects.filter(
        appointment_date=tomorrow,
        status='scheduled',
        reminder_sent=False
    )
    
    sent_count = 0
    for appointment in appointments:
        # Send email reminder
        EmailNotificationService.send_appointment_confirmation(appointment)
        
        # Send SMS reminder
        SMSNotificationService.send_appointment_reminder(appointment)
        
        # Mark reminder as sent
        appointment.reminder_sent = True
        appointment.save()
        sent_count += 1
    
    return f"Sent {sent_count} appointment reminders"

@shared_task
def mark_expired_units():
    """Mark expired blood units daily"""
    from .utils import InventoryManager
    expired_count = InventoryManager.mark_expired_units()
    return f"Marked {expired_count} units as expired"

@shared_task
def send_low_stock_alert(blood_type):
    """Send low stock alert to admins"""
    from .models import BloodInventory, CustomUser
    
    inventory = BloodInventory.objects.get(blood_type=blood_type)
    admins = CustomUser.objects.filter(role='admin')
    
    subject = f"⚠️ Low Stock Alert: {blood_type}"
    message = (
        f"Blood type {blood_type} is running low.\n"
        f"Current stock: {inventory.units_available} units\n"
        f"Threshold: {inventory.minimum_threshold} units\n"
        f"Please take action to replenish supplies."
    )
    
    sent_count = 0
    for admin in admins:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=False
            )
            sent_count += 1
        except:
            pass
    
    # Update alert timestamp
    inventory.alert_sent_at = timezone.now()
    inventory.save()
    
    return f"Sent low stock alert to {sent_count} admins"
```

#### Views for Notification Management

**Notification Preferences View**
```python
@login_required
def notification_preferences(request):
    """User notification preferences management"""
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully')
            return redirect('user_dashboard')
    else:
        form = NotificationPreferenceForm(instance=prefs)
    
    return render(request, 'notifications/preferences.html', {'form': form})
```

**Admin Urgent Notification View**
```python
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def send_urgent_blood_notification(request):
    """Admin interface to send urgent blood notifications"""
    if request.method == 'POST':
        blood_type = request.POST.get('blood_type')
        urgency = request.POST.get('urgency', 'high')
        
        # Get matching donors
        donors = Donor.objects.filter(
            blood_type=blood_type,
            is_available=True
        )
        
        # Send notifications
        sent_count = EmailNotificationService.send_urgent_blood_notification(
            donors, blood_type, urgency
        )
        
        messages.success(request, f'Sent urgent notification to {sent_count} donors')
        return redirect('admin_dashboard')
    
    return render(request, 'notifications/send_urgent.html', {
        'blood_types': BLOOD_TYPE_CHOICES
    })
```


### Feature 3: Donor Eligibility Checker

#### Database Models

**DonorEligibility Model** (New)
```python
class DonorEligibility(models.Model):
    """Track donor eligibility status and history"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, 
                             related_name='eligibility_checks')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                            related_name='eligibility_checks', null=True)
    
    # Eligibility status
    is_eligible = models.BooleanField(default=False)
    check_date = models.DateTimeField(auto_now_add=True)
    next_eligible_date = models.DateField(null=True, blank=True)
    
    # Questionnaire responses
    age = models.IntegerField()
    weight_kg = models.FloatField()
    last_donation_date = models.DateField(null=True, blank=True)
    
    # Health screening
    has_anemia = models.BooleanField(default=False)
    has_blood_pressure_issues = models.BooleanField(default=False)
    recent_illness = models.BooleanField(default=False)
    recent_illness_details = models.TextField(blank=True)
    on_medication = models.BooleanField(default=False)
    medication_details = models.TextField(blank=True)
    
    # Additional health conditions
    has_chronic_disease = models.BooleanField(default=False)
    chronic_disease_details = models.TextField(blank=True)
    recent_surgery = models.BooleanField(default=False)
    recent_tattoo_piercing = models.BooleanField(default=False)
    pregnant_or_nursing = models.BooleanField(default=False)
    
    # Ineligibility reasons
    ineligibility_reasons = models.JSONField(default=list, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-check_date']
        indexes = [
            models.Index(fields=['donor', 'is_eligible']),
            models.Index(fields=['check_date']),
        ]
    
    def __str__(self):
        status = "Eligible" if self.is_eligible else "Ineligible"
        return f"{self.donor} - {status} ({self.check_date.date()})"
```

#### Eligibility Checker Service

**Eligibility Validation Logic**
```python
from datetime import date, timedelta

class EligibilityChecker:
    """Centralized eligibility validation logic"""
    
    # Eligibility criteria constants
    MIN_AGE = 18
    MAX_AGE = 65
    MIN_WEIGHT_KG = 50
    MALE_DONATION_INTERVAL_DAYS = 56
    FEMALE_DONATION_INTERVAL_DAYS = 84
    ILLNESS_WAITING_DAYS = 14
    
    @staticmethod
    def check_age_eligibility(age):
        """Check if age meets requirements"""
        if age < EligibilityChecker.MIN_AGE:
            return False, f"Must be at least {EligibilityChecker.MIN_AGE} years old"
        if age > EligibilityChecker.MAX_AGE:
            return False, f"Must be {EligibilityChecker.MAX_AGE} years or younger"
        return True, None
    
    @staticmethod
    def check_weight_eligibility(weight_kg):
        """Check if weight meets requirements"""
        if weight_kg < EligibilityChecker.MIN_WEIGHT_KG:
            return False, f"Must weigh at least {EligibilityChecker.MIN_WEIGHT_KG} kg"
        return True, None
    
    @staticmethod
    def check_donation_interval(last_donation_date, gender):
        """Check if enough time has passed since last donation"""
        if not last_donation_date:
            return True, None
        
        interval_days = (
            EligibilityChecker.MALE_DONATION_INTERVAL_DAYS 
            if gender == 'male' 
            else EligibilityChecker.FEMALE_DONATION_INTERVAL_DAYS
        )
        
        days_since_donation = (date.today() - last_donation_date).days
        
        if days_since_donation < interval_days:
            days_remaining = interval_days - days_since_donation
            next_eligible = date.today() + timedelta(days=days_remaining)
            return False, f"Must wait {days_remaining} more days (eligible on {next_eligible})"
        
        return True, None
    
    @staticmethod
    def check_health_conditions(eligibility_data):
        """Check health conditions for disqualifying factors"""
        reasons = []
        
        if eligibility_data.get('has_anemia'):
            reasons.append("Anemia detected - not eligible to donate")
        
        if eligibility_data.get('has_blood_pressure_issues'):
            reasons.append("Blood pressure concerns - consult physician")
        
        if eligibility_data.get('recent_illness'):
            reasons.append(f"Recent illness within {EligibilityChecker.ILLNESS_WAITING_DAYS} days")
        
        if eligibility_data.get('has_chronic_disease'):
            reasons.append("Chronic disease - medical clearance required")
        
        if eligibility_data.get('recent_surgery'):
            reasons.append("Recent surgery - must wait for recovery")
        
        if eligibility_data.get('recent_tattoo_piercing'):
            reasons.append("Recent tattoo/piercing - must wait 6 months")
        
        if eligibility_data.get('pregnant_or_nursing'):
            reasons.append("Pregnant or nursing - not eligible")
        
        if eligibility_data.get('on_medication'):
            reasons.append("On medication - medical review required")
        
        return len(reasons) == 0, reasons
    
    @staticmethod
    def calculate_eligibility(donor, questionnaire_data):
        """Calculate overall eligibility from questionnaire data"""
        reasons = []
        is_eligible = True
        next_eligible_date = None
        
        # Check age
        age_eligible, age_reason = EligibilityChecker.check_age_eligibility(
            questionnaire_data['age']
        )
        if not age_eligible:
            is_eligible = False
            reasons.append(age_reason)
        
        # Check weight
        weight_eligible, weight_reason = EligibilityChecker.check_weight_eligibility(
            questionnaire_data['weight_kg']
        )
        if not weight_eligible:
            is_eligible = False
            reasons.append(weight_reason)
        
        # Check donation interval
        interval_eligible, interval_reason = EligibilityChecker.check_donation_interval(
            questionnaire_data.get('last_donation_date'),
            donor.gender
        )
        if not interval_eligible:
            is_eligible = False
            reasons.append(interval_reason)
            # Calculate next eligible date
            interval_days = (
                EligibilityChecker.MALE_DONATION_INTERVAL_DAYS 
                if donor.gender == 'male' 
                else EligibilityChecker.FEMALE_DONATION_INTERVAL_DAYS
            )
            if questionnaire_data.get('last_donation_date'):
                next_eligible_date = (
                    questionnaire_data['last_donation_date'] + 
                    timedelta(days=interval_days)
                )
        
        # Check health conditions
        health_eligible, health_reasons = EligibilityChecker.check_health_conditions(
            questionnaire_data
        )
        if not health_eligible:
            is_eligible = False
            reasons.extend(health_reasons)
        
        return {
            'is_eligible': is_eligible,
            'reasons': reasons,
            'next_eligible_date': next_eligible_date,
        }
```

#### Forms

**Eligibility Questionnaire Form**
```python
class EligibilityQuestionnaireForm(forms.ModelForm):
    """Donor eligibility pre-screening questionnaire"""
    
    class Meta:
        model = DonorEligibility
        fields = [
            'age', 'weight_kg', 'last_donation_date',
            'has_anemia', 'has_blood_pressure_issues',
            'recent_illness', 'recent_illness_details',
            'on_medication', 'medication_details',
            'has_chronic_disease', 'chronic_disease_details',
            'recent_surgery', 'recent_tattoo_piercing',
            'pregnant_or_nursing', 'notes'
        ]
        widgets = {
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'min': 1, 'max': 120}),
            'weight_kg': forms.NumberInput(attrs={'min': 1, 'step': '0.1'}),
            'recent_illness_details': forms.Textarea(attrs={'rows': 2}),
            'medication_details': forms.Textarea(attrs={'rows': 2}),
            'chronic_disease_details': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'has_anemia': 'Do you have anemia or low iron levels?',
            'has_blood_pressure_issues': 'Do you have blood pressure concerns?',
            'recent_illness': 'Have you been ill in the past 14 days?',
            'on_medication': 'Are you currently taking any medication?',
            'has_chronic_disease': 'Do you have any chronic diseases?',
            'recent_surgery': 'Have you had surgery in the past 6 months?',
            'recent_tattoo_piercing': 'Have you gotten a tattoo or piercing in the past 6 months?',
            'pregnant_or_nursing': 'Are you pregnant or nursing?',
        }
    
    def __init__(self, *args, **kwargs):
        self.donor = kwargs.pop('donor', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill from donor profile if available
        if self.donor and not self.instance.pk:
            if self.donor.date_of_birth:
                age = (date.today() - self.donor.date_of_birth).days // 365
                self.initial['age'] = age
            if self.donor.last_donation_date:
                self.initial['last_donation_date'] = self.donor.last_donation_date
        
        # Hide pregnant/nursing for male donors
        if self.donor and self.donor.gender == 'male':
            self.fields['pregnant_or_nursing'].widget = forms.HiddenInput()
            self.initial['pregnant_or_nursing'] = False
```

#### Views

**Eligibility Check View**
```python
@login_required
def check_eligibility(request):
    """Donor eligibility pre-screening"""
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, 'Please complete donor registration first')
        return redirect('register_donor')
    
    if request.method == 'POST':
        form = EligibilityQuestionnaireForm(request.POST, donor=donor)
        if form.is_valid():
            eligibility = form.save(commit=False)
            eligibility.donor = donor
            eligibility.user = request.user
            
            # Calculate eligibility
            questionnaire_data = {
                'age': eligibility.age,
                'weight_kg': eligibility.weight_kg,
                'last_donation_date': eligibility.last_donation_date,
                'has_anemia': eligibility.has_anemia,
                'has_blood_pressure_issues': eligibility.has_blood_pressure_issues,
                'recent_illness': eligibility.recent_illness,
                'on_medication': eligibility.on_medication,
                'has_chronic_disease': eligibility.has_chronic_disease,
                'recent_surgery': eligibility.recent_surgery,
                'recent_tattoo_piercing': eligibility.recent_tattoo_piercing,
                'pregnant_or_nursing': eligibility.pregnant_or_nursing,
            }
            
            result = EligibilityChecker.calculate_eligibility(donor, questionnaire_data)
            
            eligibility.is_eligible = result['is_eligible']
            eligibility.ineligibility_reasons = result['reasons']
            eligibility.next_eligible_date = result['next_eligible_date']
            eligibility.save()
            
            # Store eligibility in session for booking flow
            request.session['eligibility_check_id'] = eligibility.id
            request.session['is_eligible'] = result['is_eligible']
            
            return redirect('eligibility_result', pk=eligibility.id)
    else:
        form = EligibilityQuestionnaireForm(donor=donor)
    
    return render(request, 'eligibility/questionnaire.html', {
        'form': form,
        'donor': donor
    })

@login_required
def eligibility_result(request, pk):
    """Display eligibility check results"""
    eligibility = get_object_or_404(DonorEligibility, pk=pk, user=request.user)
    
    context = {
        'eligibility': eligibility,
        'can_book': eligibility.is_eligible,
    }
    
    return render(request, 'eligibility/result.html', context)
```

**Integrated Appointment Booking with Eligibility**
```python
@login_required
def book_appointment(request):
    """Book appointment with eligibility check integration"""
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, 'Please complete donor registration first')
        return redirect('register_donor')
    
    # Check if eligibility check exists and is recent (within 30 days)
    recent_check = DonorEligibility.objects.filter(
        donor=donor,
        check_date__gte=timezone.now() - timedelta(days=30)
    ).order_by('-check_date').first()
    
    if not recent_check or not recent_check.is_eligible:
        messages.warning(request, 'Please complete eligibility screening first')
        return redirect('check_eligibility')
    
    # Proceed with appointment booking
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = donor
            appointment.user = request.user
            appointment.save()
            
            # Send confirmation
            EmailNotificationService.send_appointment_confirmation(appointment)
            
            messages.success(request, 'Appointment booked successfully!')
            return redirect('my_appointments')
    else:
        form = AppointmentBookingForm()
    
    return render(request, 'appointments/book.html', {
        'form': form,
        'donor': donor,
        'eligibility': recent_check
    })
```


## Data Models

### Entity Relationship Diagram

```
┌─────────────────┐
│   CustomUser    │
│  (existing)     │
└────────┬────────┘
         │ 1
         │
         │ 1
┌────────┴────────┐         ┌──────────────────┐
│     Donor       │────────▶│ DonorEligibility │
│   (existing)    │ 1     * │     (new)        │
└────────┬────────┘         └──────────────────┘
         │ 1
         │
         │ *
┌────────┴────────┐         ┌──────────────────┐
│  BloodDonation  │────────▶│    BloodUnit     │
│   (existing)    │ 1     * │     (new)        │
└─────────────────┘         └────────┬─────────┘
                                     │
                                     │ *
                            ┌────────┴─────────┐
                            │  BloodInventory  │
                            │   (enhanced)     │
                            └──────────────────┘

┌─────────────────┐         ┌──────────────────┐
│   CustomUser    │────────▶│  Notification    │
│   (existing)    │ 1     1 │   Preference     │
└────────┬────────┘         │     (new)        │
         │ 1                └──────────────────┘
         │
         │ *
┌────────┴────────┐
│ NotificationLog │
│     (new)       │
└─────────────────┘

┌─────────────────┐
│ DonationAppoint │
│      ment       │
│   (existing)    │
└─────────────────┘
```

### Database Schema

**New Tables:**

1. **blood_unit**
   - id (PK)
   - blood_type (FK to blood_type_choices)
   - donation_id (FK to blood_donation, nullable)
   - donation_date (DATE)
   - expiration_date (DATE)
   - status (VARCHAR: available, reserved, used, expired, discarded)
   - unit_number (VARCHAR, unique)
   - volume_ml (INT, default 450)
   - storage_location (VARCHAR)
   - notes (TEXT)
   - created_at (DATETIME)
   - updated_at (DATETIME)
   - Indexes: (blood_type, status), (expiration_date)

2. **notification_preference**
   - id (PK)
   - user_id (FK to custom_user, unique)
   - email_enabled (BOOLEAN, default TRUE)
   - sms_enabled (BOOLEAN, default FALSE)
   - urgent_blood_email (BOOLEAN, default TRUE)
   - urgent_blood_sms (BOOLEAN, default FALSE)
   - appointment_reminder_email (BOOLEAN, default TRUE)
   - appointment_reminder_sms (BOOLEAN, default TRUE)
   - booking_confirmation_email (BOOLEAN, default TRUE)
   - booking_confirmation_sms (BOOLEAN, default FALSE)
   - request_status_email (BOOLEAN, default TRUE)
   - request_status_sms (BOOLEAN, default FALSE)
   - low_stock_email (BOOLEAN, default TRUE)
   - low_stock_sms (BOOLEAN, default FALSE)
   - created_at (DATETIME)
   - updated_at (DATETIME)

3. **notification_log**
   - id (PK)
   - user_id (FK to custom_user)
   - notification_type (VARCHAR)
   - channel (VARCHAR: email, sms, in_app)
   - recipient (VARCHAR)
   - subject (VARCHAR)
   - message (TEXT)
   - status (VARCHAR: pending, sent, failed, bounced)
   - error_message (TEXT)
   - external_id (VARCHAR)
   - sent_at (DATETIME, nullable)
   - created_at (DATETIME)
   - Indexes: (user_id, notification_type), (status, created_at)

4. **donor_eligibility**
   - id (PK)
   - donor_id (FK to donor)
   - user_id (FK to custom_user, nullable)
   - is_eligible (BOOLEAN, default FALSE)
   - check_date (DATETIME)
   - next_eligible_date (DATE, nullable)
   - age (INT)
   - weight_kg (FLOAT)
   - last_donation_date (DATE, nullable)
   - has_anemia (BOOLEAN, default FALSE)
   - has_blood_pressure_issues (BOOLEAN, default FALSE)
   - recent_illness (BOOLEAN, default FALSE)
   - recent_illness_details (TEXT)
   - on_medication (BOOLEAN, default FALSE)
   - medication_details (TEXT)
   - has_chronic_disease (BOOLEAN, default FALSE)
   - chronic_disease_details (TEXT)
   - recent_surgery (BOOLEAN, default FALSE)
   - recent_tattoo_piercing (BOOLEAN, default FALSE)
   - pregnant_or_nursing (BOOLEAN, default FALSE)
   - ineligibility_reasons (JSON)
   - notes (TEXT)
   - Indexes: (donor_id, is_eligible), (check_date)

**Enhanced Tables:**

1. **blood_inventory** (add columns)
   - critical_threshold (INT, default 2)
   - optimal_level (INT, default 20)
   - alert_sent_at (DATETIME, nullable)

### Migration Strategy

**Migration Order:**
1. Create BloodUnit model
2. Enhance BloodInventory model
3. Create NotificationPreference model
4. Create NotificationLog model
5. Create DonorEligibility model
6. Create default NotificationPreference for existing users
7. Initialize BloodInventory thresholds if not set

**Data Migration Considerations:**
- Existing BloodInventory records will get default values for new fields
- Create NotificationPreference records for all existing users with default settings
- No data loss - all migrations are additive


## Integration Points

### Integration with Existing Systems

#### 1. Donor Management Integration

**BloodUnit ↔ BloodDonation**
- When a BloodDonation is approved, automatically create BloodUnit records
- Link BloodUnit to the source BloodDonation for traceability
- Update donor's last_donation_date when donation is approved

**DonorEligibility ↔ Donor**
- Pre-fill eligibility questionnaire from Donor profile data
- Use Donor.last_donation_date for interval validation
- Use Donor.gender for gender-specific donation intervals
- Store eligibility history linked to Donor

#### 2. Appointment System Integration

**Eligibility Check → Appointment Booking**
- Require recent eligibility check (within 30 days) before booking
- Block appointment booking if donor is ineligible
- Display next eligible date if temporarily ineligible
- Pass eligibility context to booking form

**Appointment → Notifications**
- Send confirmation email/SMS immediately after booking
- Schedule reminder 24 hours before appointment
- Mark reminder as sent to avoid duplicates
- Include calendar attachment (ICS) in confirmation email

#### 3. Inventory Management Integration

**BloodDonation → BloodInventory**
- Approved donation creates BloodUnit
- BloodUnit creation updates BloodInventory.units_available
- Automatic expiration date calculation (donation_date + 42 days)
- Real-time inventory count updates

**BloodInventory → Notifications**
- Low stock detection triggers admin alerts
- Rate limiting: one alert per blood type per 24 hours
- Alert includes current stock, threshold, and blood type
- Urgent blood notifications to matching donors

#### 4. Blood Request Integration

**BloodRequest Status → Notifications**
- Approved request sends email to requester
- Rejected request sends email with rejection reason
- Status changes logged in NotificationLog
- Respect user notification preferences

**BloodRequest → Inventory**
- Display current stock levels when creating request
- Validate requested units against available stock
- Reserve units when request is approved
- Update inventory when request is fulfilled

#### 5. User Authentication Integration

**CustomUser → NotificationPreference**
- Create default preferences on user registration
- One-to-one relationship ensures single preference record
- Preferences accessible from user dashboard
- Admin users get low_stock notifications by default

**CustomUser → NotificationLog**
- All notifications linked to user for audit trail
- User can view notification history
- Track delivery success/failure per user
- Support for debugging notification issues

### URL Routing Structure

```python
# Inventory Management URLs
path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
path('inventory/add-unit/', views.add_blood_unit, name='add_blood_unit'),
path('inventory/expiration/', views.expiration_list, name='expiration_list'),
path('inventory/api/', views.inventory_api, name='inventory_api'),
path('inventory/configure/', views.configure_thresholds, name='configure_thresholds'),

# Notification URLs
path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
path('notifications/send-urgent/', views.send_urgent_blood_notification, name='send_urgent_notification'),
path('notifications/history/', views.notification_history, name='notification_history'),

# Eligibility URLs
path('eligibility/check/', views.check_eligibility, name='check_eligibility'),
path('eligibility/result/<int:pk>/', views.eligibility_result, name='eligibility_result'),
path('eligibility/history/', views.eligibility_history, name='eligibility_history'),
```

### Template Structure

```
templates/
├── inventory/
│   ├── dashboard.html          # Main inventory dashboard with charts
│   ├── add_unit.html           # Add blood unit form
│   ├── expiration_list.html    # Units sorted by expiration
│   └── configure_thresholds.html # Configure stock thresholds
├── notifications/
│   ├── preferences.html        # User notification preferences
│   ├── send_urgent.html        # Admin urgent notification form
│   ├── history.html            # Notification history
│   ├── urgent_blood_email.html # Email template: urgent blood
│   ├── urgent_blood_email.txt  # Plain text version
│   ├── appointment_confirmation.html # Email template: confirmation
│   ├── appointment_confirmation.txt  # Plain text version
│   ├── request_status_email.html # Email template: request status
│   └── request_status_email.txt  # Plain text version
└── eligibility/
    ├── questionnaire.html      # Eligibility questionnaire form
    ├── result.html             # Eligibility check results
    └── history.html            # Eligibility check history
```

### Static Assets

**JavaScript:**
- `inventory-charts.js`: Chart.js configuration for inventory visualization
- `inventory-realtime.js`: AJAX polling for real-time inventory updates
- `notification-preferences.js`: Toggle notification preferences UI

**CSS:**
- Extend existing `design-system.css` with inventory-specific styles
- Chart color scheme matching red/blood theme
- Status indicators (critical: red, low: yellow, adequate: green)

### Admin Interface Integration

**Django Admin Customization:**
```python
@admin.register(BloodUnit)
class BloodUnitAdmin(admin.ModelAdmin):
    list_display = ['unit_number', 'blood_type', 'status', 'expiration_date', 'is_expiring_soon']
    list_filter = ['blood_type', 'status', 'expiration_date']
    search_fields = ['unit_number']
    date_hierarchy = 'donation_date'

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'channel', 'status', 'sent_at']
    list_filter = ['notification_type', 'channel', 'status']
    search_fields = ['user__username', 'recipient']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'sent_at']

@admin.register(DonorEligibility)
class DonorEligibilityAdmin(admin.ModelAdmin):
    list_display = ['donor', 'is_eligible', 'check_date', 'next_eligible_date']
    list_filter = ['is_eligible', 'check_date']
    search_fields = ['donor__first_name', 'donor__last_name']
    date_hierarchy = 'check_date'
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies and consolidations:

**Redundancy Analysis:**
- Properties 1.2 and 1.3 (increment/decrement inventory) can be combined into a single property about inventory updates maintaining correct counts
- Properties 7.1 and 7.2 (SMS and email reminders) can be combined into a single property about reminder delivery
- Properties 14.1 and 14.2 (male/female donation intervals) can be combined into a single property with gender-specific logic
- Properties 15.1 and 15.2 (age min/max) can be combined into a single age range property
- Properties 9.1 and 9.2 (approved/rejected notifications) can be combined into a single property about status change notifications
- Multiple notification content properties (6.2, 7.3, 8.2, 9.3, 10.2) can be consolidated into fewer properties about required fields

**Consolidated Properties:**
After reflection, I've reduced the testable properties from 60+ to 35 focused properties that provide unique validation value without redundancy.

### Property 1: Inventory Update Correctness

For any blood donation that is approved or blood request that is fulfilled, the inventory count for that blood type should be updated to reflect the correct number of available units.

**Validates: Requirements 1.2, 1.3**

### Property 2: Real-Time Inventory API Accuracy

For any inventory query via the API, the returned data should match the current database state without requiring page refresh.

**Validates: Requirements 1.5**

### Property 3: Blood Unit Expiration Date Recording

For any blood unit added to inventory, an expiration date must be recorded and must be a valid future date.

**Validates: Requirements 2.1**

### Property 4: Expiring Soon Flag Accuracy

For any blood unit, if the current date is within 7 days of the expiration date, the unit should be flagged as expiring soon.

**Validates: Requirements 2.3**

### Property 5: Expired Unit Marking

For any blood unit with an expiration date in the past, the unit should be marked as expired.

**Validates: Requirements 2.4**

### Property 6: Expiration Date Sorting

For any collection of blood units, when sorted by expiration date, the earliest expiration date should appear first.

**Validates: Requirements 2.5**

### Property 7: Low Stock Alert Generation

For any blood type where the quantity falls below the configured threshold, a low stock alert should be generated.

**Validates: Requirements 3.2**

### Property 8: Admin Notification on Low Stock

For any low stock alert generated, email notifications should be sent to all admin users.

**Validates: Requirements 3.3**

### Property 9: Threshold Configuration Persistence

For any blood type, when an admin configures a stock threshold value, that value should be persisted and retrievable.

**Validates: Requirements 3.5**

### Property 10: Stock Status Color Coding

For any inventory item, the color code assigned should correctly reflect its status: critical (red) when at or below critical threshold, low (yellow) when at or below minimum threshold, adequate (green) when above minimum but below optimal, optimal (green) when at or above optimal level.

**Validates: Requirements 4.2**

### Property 11: Admin-Only Inventory Modification

For any non-admin user attempting to modify inventory, the system should deny access and return an authorization error.

**Validates: Requirements 5.1**

### Property 12: Authenticated User View Access

For any authenticated user (regardless of role), viewing current stock levels should be permitted.

**Validates: Requirements 5.3**

### Property 13: Inventory Modification Logging

For any inventory modification operation, a log entry should be created containing the user identification and timestamp.

**Validates: Requirements 5.4**

### Property 14: Urgent Blood Notification to Matching Donors

For any urgent blood request for a specific blood type, email notifications should be sent to all donors with matching blood type who have not disabled urgent blood notifications.

**Validates: Requirements 6.1**

### Property 15: Notification Content Completeness

For any notification sent (urgent blood, appointment, request status, low stock), the notification content should include all required fields specific to that notification type.

**Validates: Requirements 6.2, 7.3, 8.2, 9.3, 10.2**

### Property 16: Notification Logging

For any notification sent or attempted, a log entry should be created with timestamp, recipient, status, and error message (if failed).

**Validates: Requirements 6.4**

### Property 17: Notification Failure Resilience

For any batch of notifications, if one notification fails, the system should log the failure and continue processing remaining recipients.

**Validates: Requirements 6.5**

### Property 18: Appointment Reminder Delivery

For any appointment that is 24 hours away, reminder notifications should be sent via all enabled channels (email and/or SMS) based on user preferences.

**Validates: Requirements 7.1, 7.2**

### Property 19: Reminder Idempotence

For any appointment, reminders should be sent exactly once, even if the reminder task runs multiple times.

**Validates: Requirements 7.4**

### Property 20: Booking Confirmation Delivery

For any successfully booked appointment, an email confirmation should be sent to the donor.

**Validates: Requirements 8.1**

### Property 21: Calendar Attachment Inclusion

For any appointment confirmation email, an ICS calendar attachment should be included.

**Validates: Requirements 8.4**

### Property 22: Request Status Notification

For any blood request status change (approved or rejected), an email notification should be sent to the requester with appropriate details.

**Validates: Requirements 9.1, 9.2**

### Property 23: Low Stock Notification Rate Limiting

For any blood type, at most one low stock notification should be sent per 24-hour period, regardless of how many times the threshold is breached.

**Validates: Requirements 10.4**

### Property 24: Notification Preference Persistence

For any user, when notification preferences are updated (email/SMS enabled, specific notification types), those preferences should be persisted and retrievable.

**Validates: Requirements 11.1, 11.2, 11.3**

### Property 25: Notification Preference Respect

For any notification, if the recipient user has disabled that notification type or channel in their preferences, the notification should not be sent via that channel.

**Validates: Requirements 11.4**

### Property 26: SMS Fallback to Email

For any notification when SMS integration is not configured or unavailable, the system should send the notification via email instead.

**Validates: Requirements 12.4**

### Property 27: Eligibility Calculation Correctness

For any donor with questionnaire responses, the eligibility calculation should correctly determine eligibility based on all criteria (age, weight, donation interval, health conditions).

**Validates: Requirements 13.3**

### Property 28: Eligibility Response Persistence

For any completed eligibility questionnaire, all responses should be saved to the donor profile with a timestamp.

**Validates: Requirements 13.5, 20.1, 20.2**

### Property 29: Donation Interval Validation

For any donor, if their last donation was within the gender-specific interval (56 days for males, 84 days for females), they should be marked as ineligible.

**Validates: Requirements 14.1, 14.2**

### Property 30: Next Eligible Date Calculation

For any donor ineligible due to donation interval, the next eligible donation date should be calculated and provided.

**Validates: Requirements 14.4**

### Property 31: Age Range Validation

For any donor with age less than 18 or greater than 65, they should be marked as ineligible.

**Validates: Requirements 15.1, 15.2**

### Property 32: Age Calculation from Birth Date

For any donor with a date of birth, the age should be correctly calculated as the number of complete years from birth date to current date.

**Validates: Requirements 15.3**

### Property 33: Weight Threshold Validation

For any donor with weight less than 50 kilograms, they should be marked as ineligible.

**Validates: Requirements 16.1**

### Property 34: Health Condition Disqualification

For any donor reporting any disqualifying health condition (anemia, blood pressure issues, recent illness, chronic disease, recent surgery, recent tattoo/piercing, pregnant/nursing, medication), they should be marked as ineligible with specific reasons provided.

**Validates: Requirements 17.5, 17.6**

### Property 35: Ineligibility Reason Display

For any ineligible donor, specific reasons for ineligibility should be provided in the eligibility result.

**Validates: Requirements 18.2, 18.4**

### Property 36: Booking Prevention for Ineligible Donors

For any donor marked as ineligible, the appointment booking function should be disabled.

**Validates: Requirements 19.1**

### Property 37: Booking Enablement for Eligible Donors

For any donor marked as eligible with a recent eligibility check (within 30 days), the appointment booking function should be enabled.

**Validates: Requirements 19.3**

### Property 38: Eligibility History Maintenance

For any donor, all eligibility assessments should be stored and retrievable in chronological order.

**Validates: Requirements 20.4**

### Property 39: Eligibility Update Persistence

For any donor updating their eligibility information, the new data should be saved and a new eligibility assessment should be created.

**Validates: Requirements 20.3**


## Error Handling

### Error Categories and Handling Strategies

#### 1. Validation Errors

**Inventory Management:**
- Invalid blood type: Return 400 Bad Request with clear error message
- Negative quantity: Reject with validation error
- Invalid expiration date (past date for new units): Reject with validation error
- Duplicate unit number: Return 409 Conflict with error message

**Eligibility Checking:**
- Missing required fields: Return form validation errors
- Invalid age/weight values: Return validation errors with acceptable ranges
- Invalid date formats: Return validation errors with expected format

**Notifications:**
- Missing recipient email/phone: Log error, skip recipient, continue processing
- Invalid email format: Validate before sending, log error if invalid
- Invalid phone number format: Validate before sending, log error if invalid

#### 2. Authorization Errors

**Access Control:**
- Non-admin accessing inventory modification: Return 403 Forbidden with message
- Unauthenticated user accessing protected resources: Redirect to login
- User accessing another user's eligibility data: Return 403 Forbidden

**Error Response Format:**
```python
{
    "error": "Authorization failed",
    "message": "You do not have permission to modify inventory",
    "code": "INSUFFICIENT_PERMISSIONS"
}
```

#### 3. External Service Errors

**Email Delivery Failures:**
- SMTP connection error: Log error, mark notification as failed, retry up to 3 times
- Invalid recipient: Log error, mark as failed, continue with other recipients
- Rate limiting: Implement exponential backoff, queue for later delivery

**SMS Delivery Failures:**
- API connection error: Log error, fall back to email notification
- Invalid phone number: Log error, mark as failed, continue processing
- Insufficient credits: Log error, notify admins, fall back to email

**Error Handling Pattern:**
```python
try:
    send_sms(user.phone_number, message)
    log_success()
except SMSProviderError as e:
    log_failure(str(e))
    fallback_to_email(user, message)
except Exception as e:
    log_critical_error(str(e))
    notify_admins_of_failure()
```

#### 4. Data Integrity Errors

**Inventory Inconsistencies:**
- Negative inventory count: Prevent at database level with CHECK constraint
- Orphaned blood units: Implement cascade deletion or soft delete
- Missing inventory records: Auto-create with default values on first access

**Eligibility Data Issues:**
- Missing donor profile: Redirect to donor registration
- Stale eligibility data: Require re-check if older than 30 days
- Conflicting eligibility records: Use most recent check

#### 5. Concurrency Errors

**Race Conditions:**
- Multiple simultaneous inventory updates: Use database transactions with row-level locking
- Duplicate notification sends: Use idempotency keys and check reminder_sent flag
- Concurrent eligibility checks: Allow multiple checks, store all in history

**Transaction Pattern:**
```python
from django.db import transaction

@transaction.atomic
def update_inventory(blood_type, quantity_change):
    inventory = BloodInventory.objects.select_for_update().get(
        blood_type=blood_type
    )
    inventory.units_available += quantity_change
    if inventory.units_available < 0:
        raise ValueError("Insufficient inventory")
    inventory.save()
```

#### 6. System Errors

**Database Errors:**
- Connection timeout: Retry with exponential backoff
- Query timeout: Optimize query or increase timeout
- Deadlock: Retry transaction up to 3 times

**Celery Task Errors:**
- Task failure: Retry with exponential backoff (max 3 retries)
- Redis connection error: Log error, fall back to synchronous execution
- Task timeout: Set reasonable timeout limits, log and alert on timeout

**Error Logging:**
```python
import logging

logger = logging.getLogger(__name__)

try:
    process_inventory_update()
except Exception as e:
    logger.error(
        f"Inventory update failed: {str(e)}",
        exc_info=True,
        extra={
            'user_id': user.id,
            'blood_type': blood_type,
            'operation': 'update_inventory'
        }
    )
    raise
```

### Error Recovery Strategies

**Graceful Degradation:**
- If SMS fails, fall back to email
- If real-time updates fail, fall back to page refresh
- If chart rendering fails, display table view

**Retry Mechanisms:**
- Email delivery: 3 retries with exponential backoff (1s, 5s, 25s)
- SMS delivery: 2 retries with 5s delay
- Database operations: 3 retries for deadlocks

**User Feedback:**
- Display clear error messages in user's language
- Provide actionable next steps
- Log errors for admin review
- Send critical error alerts to admins


## Testing Strategy

### Dual Testing Approach

This feature will employ both unit testing and property-based testing to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property tests**: Verify universal properties across all inputs through randomization

Both approaches are complementary and necessary. Unit tests catch concrete bugs and verify specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing Configuration

**Library Selection:**
- Python: **Hypothesis** (industry-standard PBT library for Python)
- Installation: `pip install hypothesis`

**Test Configuration:**
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: blood-management-enhancements, Property {number}: {property_text}`

**Example Property Test Structure:**
```python
from hypothesis import given, strategies as st
from datetime import date, timedelta

# Feature: blood-management-enhancements, Property 4: Expiring Soon Flag Accuracy
@given(
    expiration_date=st.dates(
        min_value=date.today() - timedelta(days=10),
        max_value=date.today() + timedelta(days=20)
    )
)
def test_expiring_soon_flag_accuracy(expiration_date):
    """For any blood unit, if current date is within 7 days of expiration, 
    unit should be flagged as expiring soon"""
    unit = BloodUnit.objects.create(
        blood_type='A+',
        donation_date=date.today() - timedelta(days=10),
        expiration_date=expiration_date,
        unit_number=f"TEST-{uuid.uuid4()}"
    )
    
    days_until_expiration = (expiration_date - date.today()).days
    expected_flag = days_until_expiration <= 7
    
    assert unit.is_expiring_soon() == expected_flag
```

### Unit Testing Strategy

**Test Organization:**
```
tests/
├── test_inventory.py           # Inventory management tests
├── test_notifications.py       # Notification service tests
├── test_eligibility.py         # Eligibility checker tests
├── test_integration.py         # Integration tests
└── test_properties.py          # Property-based tests
```

**Unit Test Focus Areas:**

1. **Specific Examples:**
   - Admin dashboard displays all 8 blood types
   - Eligibility questionnaire shows correct fields
   - Notification preferences page is accessible

2. **Edge Cases:**
   - Empty inventory (0 units)
   - Donor exactly at age boundary (18 or 65)
   - Donor exactly at weight boundary (50kg)
   - Appointment exactly 24 hours away
   - Blood unit expiring today

3. **Error Conditions:**
   - Non-admin attempting inventory modification
   - Invalid email address in notification
   - Missing required eligibility fields
   - SMS provider unavailable
   - Database connection failure

4. **Integration Points:**
   - Approved donation creates blood unit
   - Blood unit creation updates inventory
   - Low stock triggers notification
   - Eligibility check blocks booking
   - Appointment booking sends confirmation

### Property-Based Testing Strategy

**Property Test Coverage:**

Each of the 39 correctness properties will have a corresponding property-based test. Here are examples for key properties:

**Property 1: Inventory Update Correctness**
```python
# Feature: blood-management-enhancements, Property 1: Inventory Update Correctness
@given(
    blood_type=st.sampled_from(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
    units_donated=st.integers(min_value=1, max_value=5)
)
def test_inventory_update_correctness(blood_type, units_donated):
    """For any approved donation, inventory count should increase correctly"""
    initial_count = BloodInventory.objects.get(blood_type=blood_type).units_available
    
    donation = create_approved_donation(blood_type, units_donated)
    InventoryManager.update_inventory_from_donation(donation)
    
    final_count = BloodInventory.objects.get(blood_type=blood_type).units_available
    assert final_count == initial_count + units_donated
```

**Property 7: Low Stock Alert Generation**
```python
# Feature: blood-management-enhancements, Property 7: Low Stock Alert Generation
@given(
    blood_type=st.sampled_from(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
    threshold=st.integers(min_value=1, max_value=20),
    quantity=st.integers(min_value=0, max_value=30)
)
def test_low_stock_alert_generation(blood_type, threshold, quantity):
    """For any blood type below threshold, alert should be generated"""
    inventory = BloodInventory.objects.get(blood_type=blood_type)
    inventory.minimum_threshold = threshold
    inventory.units_available = quantity
    inventory.save()
    
    should_alert = quantity < threshold
    alert_generated = inventory.is_low_stock()
    
    assert alert_generated == should_alert
```

**Property 25: Notification Preference Respect**
```python
# Feature: blood-management-enhancements, Property 25: Notification Preference Respect
@given(
    notification_type=st.sampled_from([
        'urgent_blood', 'appointment_reminder', 'booking_confirmation',
        'request_status', 'low_stock'
    ]),
    email_enabled=st.booleans(),
    sms_enabled=st.booleans()
)
def test_notification_preference_respect(notification_type, email_enabled, sms_enabled):
    """For any notification, disabled channels should not be used"""
    user = create_test_user()
    prefs = NotificationPreference.objects.create(user=user)
    setattr(prefs, f'{notification_type}_email', email_enabled)
    setattr(prefs, f'{notification_type}_sms', sms_enabled)
    prefs.save()
    
    channels = prefs.get_enabled_channels(notification_type)
    
    if email_enabled:
        assert 'email' in channels
    else:
        assert 'email' not in channels
    
    if sms_enabled:
        assert 'sms' in channels
    else:
        assert 'sms' not in channels
```

**Property 27: Eligibility Calculation Correctness**
```python
# Feature: blood-management-enhancements, Property 27: Eligibility Calculation Correctness
@given(
    age=st.integers(min_value=10, max_value=80),
    weight_kg=st.floats(min_value=30.0, max_value=150.0),
    has_anemia=st.booleans(),
    has_blood_pressure_issues=st.booleans(),
    recent_illness=st.booleans()
)
def test_eligibility_calculation_correctness(age, weight_kg, has_anemia, 
                                            has_blood_pressure_issues, recent_illness):
    """For any questionnaire responses, eligibility should be correctly calculated"""
    donor = create_test_donor(gender='male')
    
    questionnaire_data = {
        'age': age,
        'weight_kg': weight_kg,
        'last_donation_date': None,
        'has_anemia': has_anemia,
        'has_blood_pressure_issues': has_blood_pressure_issues,
        'recent_illness': recent_illness,
        'on_medication': False,
        'has_chronic_disease': False,
        'recent_surgery': False,
        'recent_tattoo_piercing': False,
        'pregnant_or_nursing': False,
    }
    
    result = EligibilityChecker.calculate_eligibility(donor, questionnaire_data)
    
    # Verify eligibility logic
    expected_eligible = (
        18 <= age <= 65 and
        weight_kg >= 50 and
        not has_anemia and
        not has_blood_pressure_issues and
        not recent_illness
    )
    
    assert result['is_eligible'] == expected_eligible
    
    if not expected_eligible:
        assert len(result['reasons']) > 0
```

**Property 29: Donation Interval Validation**
```python
# Feature: blood-management-enhancements, Property 29: Donation Interval Validation
@given(
    gender=st.sampled_from(['male', 'female']),
    days_since_donation=st.integers(min_value=0, max_value=120)
)
def test_donation_interval_validation(gender, days_since_donation):
    """For any donor, recent donation within interval should mark as ineligible"""
    donor = create_test_donor(gender=gender)
    last_donation_date = date.today() - timedelta(days=days_since_donation)
    
    interval_days = 56 if gender == 'male' else 84
    expected_eligible = days_since_donation >= interval_days
    
    is_eligible, reason = EligibilityChecker.check_donation_interval(
        last_donation_date, gender
    )
    
    assert is_eligible == expected_eligible
    
    if not expected_eligible:
        assert reason is not None
        assert 'wait' in reason.lower()
```

### Test Data Management

**Fixtures:**
```python
@pytest.fixture
def sample_blood_types():
    """Create inventory records for all blood types"""
    for blood_type, _ in BLOOD_TYPE_CHOICES:
        BloodInventory.objects.get_or_create(
            blood_type=blood_type,
            defaults={'units_available': 10, 'minimum_threshold': 5}
        )

@pytest.fixture
def sample_donor():
    """Create a test donor"""
    user = CustomUser.objects.create_user(
        username='testdonor',
        email='donor@test.com',
        role='donor'
    )
    return Donor.objects.create(
        user=user,
        first_name='Test',
        last_name='Donor',
        email='donor@test.com',
        phone_number='+1234567890',
        blood_type='A+',
        date_of_birth=date(1990, 1, 1),
        gender='male',
        address='123 Test St',
        city='Test City',
        state='Test State'
    )

@pytest.fixture
def admin_user():
    """Create an admin user"""
    return CustomUser.objects.create_user(
        username='admin',
        email='admin@test.com',
        role='admin',
        is_staff=True
    )
```

### Integration Testing

**Test Scenarios:**

1. **End-to-End Donation Flow:**
   - Donor checks eligibility → passes → books appointment → receives confirmation → donates → donation approved → inventory updated → low stock detected → admins notified

2. **Urgent Blood Request Flow:**
   - Admin sends urgent notification → matching donors receive email/SMS → donor responds → appointment booked → donation completed

3. **Expiration Management Flow:**
   - Blood units added → time passes → units flagged as expiring soon → units expire → inventory updated → low stock alert triggered

### Performance Testing

**Load Testing Scenarios:**
- 100 concurrent inventory updates
- 1000 notification sends in batch
- 50 simultaneous eligibility checks

**Performance Targets:**
- Inventory dashboard load: < 2 seconds
- API response time: < 500ms
- Notification batch processing: < 5 seconds for 100 recipients
- Eligibility calculation: < 100ms

### Continuous Integration

**CI Pipeline:**
```yaml
test:
  script:
    - pip install -r requirements.txt
    - python manage.py test --settings=backend.test_settings
    - pytest tests/ --hypothesis-profile=ci
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

**Hypothesis CI Profile:**
```python
from hypothesis import settings, Verbosity

settings.register_profile("ci", max_examples=200, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=100)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)
```

### Test Coverage Goals

- Overall code coverage: > 85%
- Critical paths (eligibility, inventory updates): > 95%
- Error handling paths: > 80%
- Property test coverage: 100% of correctness properties


## Deployment Strategy

### PythonAnywhere Deployment Steps

**1. Database Migrations**
```bash
# On PythonAnywhere console
cd ~/blood-management-system
source venv/bin/activate

# Create migrations
python manage.py makemigrations

# Review migrations
python manage.py sqlmigrate core_blood_system 000X

# Apply migrations
python manage.py migrate

# Create default notification preferences for existing users
python manage.py shell
>>> from core_blood_system.models import CustomUser, NotificationPreference
>>> for user in CustomUser.objects.all():
...     NotificationPreference.objects.get_or_create(user=user)
```

**2. Static Files**
```bash
# Collect static files including new Chart.js assets
python manage.py collectstatic --noinput
```

**3. Dependencies Installation**
```bash
# Install new dependencies
pip install celery redis hypothesis twilio africastalking

# Update requirements.txt
pip freeze > requirements.txt
```

**4. Environment Configuration**
```python
# Add to settings.py or environment variables

# Email Configuration (already configured for PythonAnywhere)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or PythonAnywhere SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'Blood Bank <noreply@bloodbank.com>'

# SMS Configuration (optional)
SMS_PROVIDER = os.environ.get('SMS_PROVIDER', None)  # 'twilio' or 'africas_talking'

# Twilio (if using)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Africa's Talking (if using)
AFRICAS_TALKING_USERNAME = os.environ.get('AFRICAS_TALKING_USERNAME')
AFRICAS_TALKING_API_KEY = os.environ.get('AFRICAS_TALKING_API_KEY')

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Blood Bank Contact Info
BLOOD_BANK_CONTACT = '+1234567890'
```

**5. Celery Setup (Optional - for scheduled tasks)**

Note: PythonAnywhere free tier doesn't support long-running processes. For scheduled tasks:

**Option A: Use PythonAnywhere Scheduled Tasks**
```python
# Create management command: management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from core_blood_system.tasks import send_appointment_reminders

class Command(BaseCommand):
    def handle(self, *args, **options):
        send_appointment_reminders()
```

Schedule in PythonAnywhere Tasks tab:
- Daily at 9:00 AM: `python manage.py send_reminders`
- Daily at midnight: `python manage.py mark_expired_units`

**Option B: Use Celery (requires paid plan)**
```bash
# Start Celery worker
celery -A backend worker -l info

# Start Celery beat scheduler
celery -A backend beat -l info
```

**6. Initialize Blood Inventory**
```bash
python manage.py shell
>>> from core_blood_system.models import BloodInventory, BLOOD_TYPE_CHOICES
>>> for blood_type, _ in BLOOD_TYPE_CHOICES:
...     BloodInventory.objects.get_or_create(
...         blood_type=blood_type,
...         defaults={
...             'units_available': 0,
...             'minimum_threshold': 5,
...             'critical_threshold': 2,
...             'optimal_level': 20
...         }
...     )
```

**7. Web App Reload**
```bash
# Reload web app from PythonAnywhere dashboard
# Or via API:
curl -X POST https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain}/reload/ \
  -H "Authorization: Token {api_token}"
```

### Deployment Checklist

- [ ] Database migrations created and applied
- [ ] Static files collected
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Email backend tested
- [ ] SMS provider configured (optional)
- [ ] Scheduled tasks configured
- [ ] Blood inventory initialized
- [ ] Admin users have notification preferences
- [ ] Web app reloaded
- [ ] Smoke tests passed

### Rollback Plan

If issues occur after deployment:

1. **Database Rollback:**
```bash
# Revert last migration
python manage.py migrate core_blood_system 000X  # Previous migration number
```

2. **Code Rollback:**
```bash
git revert HEAD
git push origin main
# Reload web app
```

3. **Data Integrity Check:**
```bash
python manage.py shell
>>> from core_blood_system.models import BloodInventory, BloodUnit
>>> # Verify inventory counts match unit counts
>>> for inv in BloodInventory.objects.all():
...     actual = BloodUnit.objects.filter(
...         blood_type=inv.blood_type, 
...         status='available'
...     ).count()
...     if actual != inv.units_available:
...         print(f"Mismatch for {inv.blood_type}: {actual} vs {inv.units_available}")
```

### Monitoring and Maintenance

**Health Checks:**
- Monitor notification delivery success rate
- Check for expired units daily
- Verify inventory counts match unit counts
- Monitor low stock alerts

**Logs to Monitor:**
- Notification failures
- Eligibility check errors
- Inventory update errors
- SMS delivery failures

**Regular Maintenance:**
- Weekly: Review notification logs for failures
- Monthly: Clean up old notification logs (> 90 days)
- Monthly: Review eligibility check history
- Quarterly: Audit inventory accuracy

### Performance Optimization

**Database Indexes:**
Already included in models:
- BloodUnit: (blood_type, status), (expiration_date)
- NotificationLog: (user, notification_type), (status, created_at)
- DonorEligibility: (donor, is_eligible), (check_date)

**Query Optimization:**
- Use select_related() for foreign key lookups
- Use prefetch_related() for reverse foreign key lookups
- Cache inventory dashboard data (5-minute cache)
- Batch notification sends (100 at a time)

**Caching Strategy:**
```python
from django.core.cache import cache

def get_inventory_data():
    cache_key = 'inventory_dashboard_data'
    data = cache.get(cache_key)
    
    if data is None:
        data = {
            'inventory': list(BloodInventory.objects.all()),
            'expiring_soon': list(BloodUnit.objects.filter(
                status='available',
                expiration_date__lte=date.today() + timedelta(days=7)
            ))
        }
        cache.set(cache_key, data, 300)  # 5 minutes
    
    return data
```

## Summary

This design document specifies the implementation of three critical enhancements to the Blood Management System:

1. **Blood Bank Inventory Management**: Real-time tracking with expiration management, automated alerts, and visual dashboards using Chart.js
2. **SMS/Email Notifications**: Multi-channel notification system with user preferences, scheduled reminders via Celery, and comprehensive logging
3. **Donor Eligibility Checker**: Pre-screening questionnaire with automated validation based on age, weight, donation intervals, and health conditions

The design maintains full compatibility with the existing Django application, follows established patterns, and includes 39 correctness properties for comprehensive testing. The implementation uses Hypothesis for property-based testing alongside traditional unit tests to ensure system correctness across all scenarios.

All features are designed for PythonAnywhere deployment with fallback options for resource-constrained environments, ensuring reliable operation while maintaining the existing red/blood theme and mobile-responsive design.

