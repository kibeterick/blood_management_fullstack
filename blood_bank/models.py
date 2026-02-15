from django.db import models
from django.contrib.auth.models import User


class BloodDonor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    medical_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.blood_type})"


class BloodBank(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    operating_hours = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=100)
    current_stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class BloodRecipient(models.Model):
    URGENCY_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    blood_type = models.CharField(max_length=3, choices=BloodDonor.BLOOD_TYPE_CHOICES)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    hospital_name = models.CharField(max_length=100)
    medical_condition = models.TextField()
    urgency_level = models.CharField(max_length=10, choices=URGENCY_LEVEL_CHOICES, default='medium')
    blood_units_required = models.PositiveIntegerField(default=1)
    date_needed = models.DateField()
    is_fulfilled = models.BooleanField(default=False)
    doctor_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.blood_type}) - {self.hospital_name}"


class BloodDonation(models.Model):
    DONATION_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(BloodDonor, on_delete=models.CASCADE)
    recipient = models.ForeignKey(BloodRecipient, on_delete=models.CASCADE, null=True, blank=True)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    donation_date = models.DateTimeField(auto_now_add=True)
    blood_units = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=DONATION_STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        recipient_name = self.recipient.name if self.recipient else "Blood Bank"
        return f"Donation from {self.donor.name} to {recipient_name}"


class BloodInventory(models.Model):
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3, choices=BloodDonor.BLOOD_TYPE_CHOICES)
    units_available = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_bank.name} - {self.blood_type}: {self.units_available} units"