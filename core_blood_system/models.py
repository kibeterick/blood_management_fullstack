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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.blood_type}"
    
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
    
    def __str__(self):
        return f"{self.blood_type}: {self.units_available} units"
    
    def is_low_stock(self):
        return self.units_available < self.minimum_threshold
    
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


# ==========================================
# ADVANCED SECURITY MODELS
# ==========================================

class TwoFactorAuth(models.Model):
    """Store 2FA secrets for users"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='two_factor')
    secret_key = models.CharField(max_length=32, unique=True)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.TextField(blank=True)  # Comma-separated backup codes
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'two_factor_auth'
        verbose_name = 'Two-Factor Authentication'
        verbose_name_plural = 'Two-Factor Authentications'
    
    def __str__(self):
        return f'2FA for {self.user.username}'


class EmailVerification(models.Model):
    """Email verification tokens"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Email verification for {self.user.username}'


class UserActivityLog(models.Model):
    """Track user activities for security and audit purposes"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('email_verified', 'Email Verified'),
        ('failed_login', 'Failed Login'),
        ('session_terminated', 'Session Terminated'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)  # City, Country
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    details = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.action} at {self.timestamp}'


class UserSession(models.Model):
    """Track active user sessions for security"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f'{self.user.username} - {self.device_info}'


class AdminAuditLog(models.Model):
    """Immutable audit log for admin actions"""
    
    admin_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='admin_actions')
    action_type = models.CharField(max_length=50)  # create, update, delete, approve, reject
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(default=dict)  # Store what changed
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'admin_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f'{self.admin_user.username} - {self.action_type} {self.model_name} #{self.object_id}'
