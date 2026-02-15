"""
Appointment Scheduling System for Blood Donations
"""
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class DonationAppointment(models.Model):
    """
    Model for scheduling blood donation appointments
    """
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
    
    donor = models.ForeignKey('Donor', on_delete=models.CASCADE, related_name='appointments')
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
        unique_together = ['appointment_date', 'time_slot', 'location']
    
    def __str__(self):
        return f"{self.donor} - {self.appointment_date} at {self.get_time_slot_display()}"
    
    def is_upcoming(self):
        """Check if appointment is in the future"""
        appointment_datetime = datetime.combine(self.appointment_date, datetime.min.time())
        return appointment_datetime >= datetime.now() and self.status in ['scheduled', 'confirmed']
    
    def can_cancel(self):
        """Check if appointment can be cancelled (at least 24 hours before)"""
        appointment_datetime = datetime.combine(self.appointment_date, datetime.min.time())
        hours_until = (appointment_datetime - datetime.now()).total_seconds() / 3600
        return hours_until >= 24 and self.status in ['scheduled', 'confirmed']


def get_available_time_slots(date, location):
    """
    Get available time slots for a specific date and location
    """
    from .appointments import DonationAppointment
    
    # Get all booked slots for this date and location
    booked_slots = DonationAppointment.objects.filter(
        appointment_date=date,
        location=location,
        status__in=['scheduled', 'confirmed']
    ).values_list('time_slot', flat=True)
    
    # Get all possible slots
    all_slots = [slot[0] for slot in DonationAppointment.TIME_SLOT_CHOICES]
    
    # Return available slots
    available = [slot for slot in all_slots if slot not in booked_slots]
    
    return available


def send_appointment_reminder(appointment):
    """
    Send reminder email/SMS for upcoming appointment
    """
    from .notifications import send_mail
    from django.conf import settings
    
    subject = f'Reminder: Blood Donation Appointment Tomorrow'
    
    message = f"""
    Dear {appointment.donor.first_name},
    
    This is a friendly reminder about your blood donation appointment:
    
    Date: {appointment.appointment_date.strftime('%B %d, %Y')}
    Time: {appointment.get_time_slot_display()}
    Location: {appointment.location}
    Address: {appointment.address}
    
    Please arrive 10 minutes early and bring a valid ID.
    
    Important reminders:
    - Eat a healthy meal before donating
    - Stay hydrated
    - Get adequate rest
    - Avoid alcohol 24 hours before donation
    
    If you need to cancel or reschedule, please contact us at least 24 hours in advance.
    
    Thank you for your commitment to saving lives!
    
    Blood Management System
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.donor.email],
            fail_silently=False,
        )
        appointment.reminder_sent = True
        appointment.save()
    except Exception as e:
        print(f"Failed to send reminder: {str(e)}")


def get_upcoming_appointments(donor):
    """
    Get all upcoming appointments for a donor
    """
    today = timezone.now().date()
    return DonationAppointment.objects.filter(
        donor=donor,
        appointment_date__gte=today,
        status__in=['scheduled', 'confirmed']
    ).order_by('appointment_date', 'time_slot')


def check_appointment_conflicts(donor, date, time_slot):
    """
    Check if donor already has an appointment at this time
    """
    return DonationAppointment.objects.filter(
        donor=donor,
        appointment_date=date,
        time_slot=time_slot,
        status__in=['scheduled', 'confirmed']
    ).exists()
