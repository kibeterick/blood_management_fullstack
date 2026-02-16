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