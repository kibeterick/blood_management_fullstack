from django.db import models
from django.contrib.auth.models import AbstractUser

# Blood type choices
BLOOD_TYPE_CHOICES = [
    ('A+', 'A Positive'),
    ('A-', 'A Negative'),
    ('B+', 'B Positive'),
    ('B-', 'B Negative'),
    ('AB+', 'AB Positive'),
    ('AB-', 'AB Negative'),
    ('O+', 'O Positive'),
    ('O-', 'O Negative'),
]

# Purpose choices for blood requests
PURPOSE_CHOICES = [
    ('surgery', 'Surgery'),
    ('emergency', 'Emergency'),
    ('accident', 'Accident'),
    ('anemia', 'Anemia Treatment'),
    ('cancer', 'Cancer Treatment'),
    ('pregnancy', 'Pregnancy Complications'),
    ('other', 'Other Medical Purpose'),
]

# User roles
USER_ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('user', 'Regular User'),
    ('donor', 'Blood Donor'),
]

# Gender choices
GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


# Custom User Model
class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


# Donor Model
# Donor Model
class Donor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    # Eligibility tracking fields
    next_eligible_date = models.DateField(null=True, blank=True, help_text="Next date donor is eligible to donate")
    is_eligible_override = models.BooleanField(default=False, help_text="Admin override for eligibility")
    eligibility_notes = models.TextField(blank=True, null=True, help_text="Notes about eligibility status")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.blood_type}"

    def calculate_next_eligible_date(self):
        """Calculate next eligible donation date (56 days from last donation)"""
        if self.last_donation_date:
            from datetime import timedelta
            return self.last_donation_date + timedelta(days=56)
        return None

    def is_eligible(self):
        """Check if donor is currently eligible to donate"""
        # Admin override takes precedence
        if self.is_eligible_override:
            return True

        # If no last donation date, donor is eligible
        if not self.last_donation_date:
            return True

        # Check if 56 days have passed since last donation
        from datetime import date
        next_eligible = self.calculate_next_eligible_date()
        if next_eligible:
            return date.today() >= next_eligible

        return True

    def days_until_eligible(self):
        """Calculate days remaining until eligible to donate"""
        if self.is_eligible():
            return 0

        from datetime import date
        next_eligible = self.calculate_next_eligible_date()
        if next_eligible:
            days = (next_eligible - date.today()).days
            return max(0, days)

        return 0

    def get_eligibility_status(self):
        """Get eligibility status with reason"""
        if self.is_eligible_override:
            return {
                'eligible': True,
                'reason': 'Admin Override',
                'badge_class': 'success',
                'icon': 'check-circle-fill'
            }

        if self.is_eligible():
            return {
                'eligible': True,
                'reason': 'Eligible to Donate',
                'badge_class': 'success',
                'icon': 'check-circle-fill'
            }
        else:
            days = self.days_until_eligible()
            next_date = self.calculate_next_eligible_date()
            return {
                'eligible': False,
                'reason': f'Wait {days} more days',
                'next_date': next_date,
                'badge_class': 'danger',
                'icon': 'x-circle-fill'
            }

    def save(self, *args, **kwargs):
        """Auto-calculate next eligible date on save"""
        if self.last_donation_date and not self.is_eligible_override:
            self.next_eligible_date = self.calculate_next_eligible_date()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']



# Blood Request Model
class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=200)
    patient_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    patient_age = models.IntegerField(null=True, blank=True, help_text="Patient age in years")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    units_needed = models.IntegerField()
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    purpose_details = models.TextField(blank=True, null=True, help_text="Additional details about the purpose")
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    required_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    
    def __str__(self):
        return f"Request for {self.blood_type} - {self.patient_name} ({self.get_purpose_display()})"
    
    class Meta:
        ordering = ['-created_at']


# Blood Donation Model
class BloodDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donation_date = models.DateField()
    units_donated = models.IntegerField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    hospital_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection (e.g., disease)")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_donations')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.donor} - {self.blood_type} on {self.donation_date} ({self.status})"
    
    class Meta:
        ordering = ['-donation_date']


# Blood Inventory Model
class BloodInventory(models.Model):
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, unique=True)
    units_available = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    minimum_threshold = models.IntegerField(default=5, help_text="Minimum units to maintain")
    critical_threshold = models.IntegerField(default=2, help_text="Critical low level")
    optimal_level = models.IntegerField(default=20, help_text="Optimal stock level")
    alert_sent_at = models.DateTimeField(null=True, blank=True, help_text="Last alert timestamp")
    
    def __str__(self):
        return f"{self.blood_type}: {self.units_available} units"
    
    def is_low_stock(self):
        return self.units_available < self.minimum_threshold
    
    def get_status(self):
        """Get inventory status"""
        if self.units_available <= self.critical_threshold:
            return 'critical'
        elif self.units_available < self.minimum_threshold:
            return 'low'
        elif self.units_available >= self.optimal_level:
            return 'optimal'
        return 'adequate'
    
    class Meta:
        verbose_name_plural = "Blood Inventories"
        ordering = ['blood_type']



# ============================================
# ENHANCEMENT MODELS - TOP 5 FEATURES
# ============================================

# 1. APPOINTMENT SCHEDULING SYSTEM
class DonationAppointment(models.Model):
    """Blood donation appointment scheduling"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    TIME_SLOT_CHOICES = [
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='appointments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_appointments', null=True, blank=True)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=TIME_SLOT_CHOICES)
    location = models.CharField(max_length=200, help_text="Hospital or donation center")
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date', 'time_slot']
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.donor} - {self.appointment_date} at {self.get_time_slot_display()}"


# 2. REAL-TIME NOTIFICATIONS SYSTEM
class Notification(models.Model):
    """In-app notification system"""
    TYPE_CHOICES = [
        ('appointment', 'Appointment'),
        ('blood_request', 'Blood Request'),
        ('donation', 'Donation'),
        ('match', 'Donor Match'),
        ('system', 'System'),
        ('urgent', 'Urgent Request'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# 3. BLOOD REQUEST MATCHING ALGORITHM
class MatchedDonor(models.Model):
    """Track matched donors for blood requests"""
    STATUS_CHOICES = [
        ('matched', 'Matched'),
        ('notified', 'Notified'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    ]
    
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='matched_donors')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='matched_requests')
    match_score = models.IntegerField(help_text="Matching score based on compatibility, distance, etc.")
    distance_km = models.FloatField(null=True, blank=True, help_text="Distance from donor to hospital")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='matched')
    notified_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_score', 'distance_km']
        unique_together = ['blood_request', 'donor']
        indexes = [
            models.Index(fields=['blood_request', 'status']),
        ]
    
    def __str__(self):
        return f"{self.donor} matched to {self.blood_request} (Score: {self.match_score})"


# 4. ANALYTICS DATA (Calculated on-the-fly, no model needed)
# Analytics will be computed in views using aggregation


# 5. QR CODE SYSTEM
class QRCode(models.Model):
    """QR codes for donors, certificates, and blood bags"""
    TYPE_CHOICES = [
        ('donor', 'Donor ID'),
        ('certificate', 'Donation Certificate'),
        ('blood_bag', 'Blood Bag'),
        ('appointment', 'Appointment'),
    ]
    
    qr_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    code = models.CharField(max_length=100, unique=True, help_text="Unique QR code string")
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, null=True, blank=True, related_name='qr_codes')
    donation = models.ForeignKey(BloodDonation, on_delete=models.CASCADE, null=True, blank=True, related_name='qr_codes')
    appointment = models.ForeignKey(DonationAppointment, on_delete=models.CASCADE, null=True, blank=True, related_name='qr_codes')
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    data = models.JSONField(help_text="Additional data encoded in QR", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    scanned_count = models.IntegerField(default=0)
    last_scanned = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['qr_type']),
        ]
    
    def __str__(self):
        return f"{self.get_qr_type_display()} - {self.code}"


# BLOOD MANAGEMENT ENHANCEMENTS - NOTIFICATION PREFERENCES
class NotificationPreference(models.Model):
    """User notification preferences for channels and types"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, 
                               related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    
    # Individual notification type preferences - Email
    urgent_blood_email = models.BooleanField(default=True, 
                                             help_text="Receive urgent blood need alerts via email")
    appointment_reminder_email = models.BooleanField(default=True,
                                                     help_text="Receive appointment reminders via email")
    appointment_confirmation_email = models.BooleanField(default=True,
                                                         help_text="Receive booking confirmations via email")
    request_status_email = models.BooleanField(default=True,
                                              help_text="Receive request status updates via email")
    low_stock_email = models.BooleanField(default=True,
                                         help_text="Receive low stock alerts via email (admin only)")
    
    # Individual notification type preferences - SMS
    urgent_blood_sms = models.BooleanField(default=False,
                                          help_text="Receive urgent blood need alerts via SMS")
    appointment_reminder_sms = models.BooleanField(default=True,
                                                   help_text="Receive appointment reminders via SMS")
    appointment_confirmation_sms = models.BooleanField(default=False,
                                                       help_text="Receive booking confirmations via SMS")
    request_status_sms = models.BooleanField(default=False,
                                            help_text="Receive request status updates via SMS")
    low_stock_sms = models.BooleanField(default=False,
                                       help_text="Receive low stock alerts via SMS (admin only)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
    
    def __str__(self):
        return f"{self.user.username} - Notification Preferences"
    
    def get_enabled_channels(self, notification_type):
        """Get enabled channels for a specific notification type"""
        channels = []
        if getattr(self, f'{notification_type}_email', False):
            channels.append('email')
        if getattr(self, f'{notification_type}_sms', False):
            channels.append('sms')
        return channels


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
    recipient = models.CharField(max_length=200, help_text="Email or phone number")
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # External service tracking
    external_id = models.CharField(max_length=100, blank=True, 
                                   help_text="Twilio SID, etc.")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        indexes = [
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type} via {self.channel}"


class BloodUnit(models.Model):
    """Individual blood unit tracking with expiration management"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('discarded', 'Discarded'),
    ]
    
    blood_type = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ])
    donation = models.ForeignKey(BloodDonation, on_delete=models.SET_NULL, 
                                null=True, blank=True, related_name='blood_units')
    donation_date = models.DateField()
    expiration_date = models.DateField(help_text="Typically 42 days from donation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    unit_number = models.CharField(max_length=50, unique=True, 
                                   help_text="Unique identifier")
    volume_ml = models.IntegerField(default=450, help_text="Standard unit volume")
    storage_location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['expiration_date', 'donation_date']
        verbose_name = "Blood Unit"
        verbose_name_plural = "Blood Units"
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
    
    def __str__(self):
        return f"{self.unit_number} - {self.blood_type} ({self.status})"


class DonorEligibility(models.Model):
    """Track donor eligibility assessments"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, 
                             related_name='eligibility_assessments')
    age = models.IntegerField()
    weight = models.FloatField(help_text="Weight in kilograms")
    last_donation_date = models.DateField(null=True, blank=True)
    
    # Health screening
    recent_illness = models.BooleanField(default=False, 
                                        help_text="Illness within last 14 days")
    current_medication = models.BooleanField(default=False)
    anemia = models.BooleanField(default=False)
    blood_pressure_issues = models.BooleanField(default=False)
    
    # Eligibility result
    is_eligible = models.BooleanField(default=False)
    ineligibility_reasons = models.TextField(blank=True)
    next_eligible_date = models.DateField(null=True, blank=True)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-assessment_date']
        verbose_name = "Donor Eligibility"
        verbose_name_plural = "Donor Eligibilities"
    
    def __str__(self):
        status = "Eligible" if self.is_eligible else "Ineligible"
        return f"{self.donor} - {status} ({self.assessment_date.date()})"
