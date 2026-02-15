from django.db import models
from django.utils import timezone
from datetime import timedelta

class Donor(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    last_donation_date = models.DateField(null=True, blank=True)
    
    @property
    def is_eligible(self):
        # Basic logic: Eligible if last donation was > 90 days ago
        if not self.last_donation_date:
            return True
        return timezone.now().date() > self.last_donation_date + timedelta(days=90)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.blood_type})"

class BloodInventory(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Transfused', 'Transfused'),
        ('Expired', 'Expired'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3)
    collection_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    def save(self, *args, **kwargs):
        # Auto-set expiry date (e.g., 42 days for red blood cells)
        if not self.expiry_date:
            self.expiry_date = timezone.now().date() + timedelta(days=42)
        super().save(*args, **kwargs)

class BloodRequest(models.Model):
    URGENCY = [('Normal', 'Normal'), ('Urgent', 'Urgent'), ('Emergency', 'Emergency')]
    
    patient_name = models.CharField(max_length=100)
    required_blood_type = models.CharField(max_length=3)
    units_requested = models.PositiveIntegerField(default=1)
    urgency_level = models.CharField(max_length=10, choices=URGENCY)
    status = models.CharField(max_length=20, default='Pending')
    hospital_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)