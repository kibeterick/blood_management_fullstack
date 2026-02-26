"""
Top 5 Enhancements - Core Logic
Blood Management System
"""
from django.db import models
from django.db.models import Count, Q, Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
from django.core.files import File
import uuid
import json


# ============================================
# 1. APPOINTMENT SCHEDULING SYSTEM
# ============================================

def get_available_time_slots(date, location):
    """Get available time slots for a specific date and location"""
    from .models import DonationAppointment
    
    booked_slots = DonationAppointment.objects.filter(
        appointment_date=date,
        location=location,
        status__in=['scheduled', 'confirmed']
    ).values_list('time_slot', flat=True)
    
    all_slots = [slot[0] for slot in DonationAppointment.TIME_SLOT_CHOICES]
    available = [slot for slot in all_slots if slot not in booked_slots]
    
    return available


def create_appointment(donor, user, date, time_slot, location, address, notes=''):
    """Create a new donation appointment"""
    from .models import DonationAppointment
    
    appointment = DonationAppointment.objects.create(
        donor=donor,
        user=user,
        appointment_date=date,
        time_slot=time_slot,
        location=location,
        address=address,
        notes=notes,
        status='scheduled'
    )
    
    # Create notification
    create_notification(
        user=user,
        notification_type='appointment',
        title='Appointment Scheduled',
        message=f'Your blood donation appointment is scheduled for {date} at {time_slot}',
        link=f'/appointments/{appointment.id}/'
    )
    
    return appointment


def send_appointment_reminders():
    """Send reminders for appointments happening tomorrow"""
    from .models import DonationAppointment
    
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    appointments = DonationAppointment.objects.filter(
        appointment_date=tomorrow,
        status__in=['scheduled', 'confirmed'],
        reminder_sent=False
    )
    
    for appointment in appointments:
        # Send email reminder
        send_email_notification(
            to_email=appointment.donor.email,
            subject='Reminder: Blood Donation Appointment Tomorrow',
            message=f"""
            Dear {appointment.donor.first_name},
            
            This is a reminder about your blood donation appointment:
            
            Date: {appointment.appointment_date}
            Time: {appointment.get_time_slot_display()}
            Location: {appointment.location}
            Address: {appointment.address}
            
            Please arrive 10 minutes early.
            
            Thank you!
            """
        )
        
        # Mark as sent
        appointment.reminder_sent = True
        appointment.save()


# ============================================
# 2. REAL-TIME NOTIFICATIONS SYSTEM
# ============================================

def create_notification(user, notification_type, title, message, link=''):
    """Create an in-app notification"""
    from .models import Notification
    
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )
    
    return notification


def get_unread_notifications(user):
    """Get unread notifications for a user"""
    from .models import Notification
    
    return Notification.objects.filter(user=user, is_read=False)


def mark_notification_read(notification_id):
    """Mark a notification as read"""
    from .models import Notification
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False


def send_email_notification(to_email, subject, message):
    """Send email notification"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email send failed: {str(e)}")
        return False


# ============================================
# 3. BLOOD REQUEST MATCHING ALGORITHM
# ============================================

def match_donors_to_request(blood_request):
    """Match compatible donors to a blood request"""
    from .models import Donor, MatchedDonor
    
    # Find compatible donors
    compatible_donors = Donor.objects.filter(
        blood_type=blood_request.blood_type,
        is_available=True
    )
    
    # Check last donation date (must be at least 56 days ago)
    min_date = timezone.now().date() - timedelta(days=56)
    eligible_donors = compatible_donors.filter(
        Q(last_donation_date__lte=min_date) | Q(last_donation_date__isnull=True)
    )
    
    matches = []
    for donor in eligible_donors:
        # Calculate match score (0-100)
        score = calculate_match_score(donor, blood_request)
        
        # Create match record
        match, created = MatchedDonor.objects.get_or_create(
            blood_request=blood_request,
            donor=donor,
            defaults={
                'match_score': score,
                'status': 'matched'
            }
        )
        
        if created:
            matches.append(match)
            
            # Notify donor
            if donor.user:
                create_notification(
                    user=donor.user,
                    notification_type='match',
                    title='Blood Request Match',
                    message=f'You match a {blood_request.get_urgency_display()} priority blood request for {blood_request.blood_type}',
                    link=f'/blood-requests/{blood_request.id}/'
                )
    
    return matches


def calculate_match_score(donor, blood_request):
    """Calculate matching score for donor-request pair"""
    score = 50  # Base score
    
    # Exact blood type match
    if donor.blood_type == blood_request.blood_type:
        score += 30
    
    # Recent donation history (bonus for regular donors)
    if donor.last_donation_date:
        days_since = (timezone.now().date() - donor.last_donation_date).days
        if 56 <= days_since <= 90:
            score += 10  # Recently eligible
        elif days_since > 365:
            score -= 5  # Long time since last donation
    
    # Location proximity (if available)
    if donor.city == blood_request.hospital_name:
        score += 10
    
    return min(score, 100)  # Cap at 100


def notify_matched_donors(blood_request):
    """Send notifications to all matched donors"""
    from .models import MatchedDonor
    
    matches = MatchedDonor.objects.filter(
        blood_request=blood_request,
        status='matched'
    ).select_related('donor')
    
    for match in matches:
        if match.donor.user:
            # Send email
            send_email_notification(
                to_email=match.donor.email,
                subject=f'{blood_request.get_urgency_display()} Blood Request Match',
                message=f"""
                Dear {match.donor.first_name},
                
                You have been matched to an urgent blood request:
                
                Blood Type: {blood_request.blood_type}
                Units Needed: {blood_request.units_needed}
                Hospital: {blood_request.hospital_name}
                Required Date: {blood_request.required_date}
                Urgency: {blood_request.get_urgency_display()}
                
                If you can donate, please contact: {blood_request.contact_number}
                
                Thank you for saving lives!
                """
            )
            
            match.status = 'notified'
            match.notified_at = timezone.now()
            match.save()


# ============================================
# 4. ADVANCED ANALYTICS DASHBOARD
# ============================================

def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    from .models import Donor, BloodRequest, BloodDonation, BloodInventory
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    analytics = {
        # Donor Statistics
        'total_donors': Donor.objects.count(),
        'active_donors': Donor.objects.filter(is_available=True).count(),
        'new_donors_this_month': Donor.objects.filter(created_at__gte=this_month_start).count(),
        
        # Blood Request Statistics
        'total_requests': BloodRequest.objects.count(),
        'pending_requests': BloodRequest.objects.filter(status='pending').count(),
        'fulfilled_requests': BloodRequest.objects.filter(status='fulfilled').count(),
        'critical_requests': BloodRequest.objects.filter(urgency='critical', status='pending').count(),
        
        # Donation Statistics
        'total_donations': BloodDonation.objects.count(),
        'donations_this_month': BloodDonation.objects.filter(donation_date__gte=this_month_start).count(),
        'donations_last_month': BloodDonation.objects.filter(
            donation_date__gte=last_month_start,
            donation_date__lt=this_month_start
        ).count(),
        'total_units_donated': BloodDonation.objects.filter(status='approved').aggregate(
            total=Sum('units_donated')
        )['total'] or 0,
        
        # Blood Type Distribution
        'blood_type_distribution': Donor.objects.values('blood_type').annotate(
            count=Count('id')
        ).order_by('-count'),
        
        # Inventory Status
        'inventory_status': list(BloodInventory.objects.all()),
        'low_stock_items': BloodInventory.objects.filter(
            units_available__lt=F('minimum_threshold')
        ).count(),
        
        # Monthly Trends (last 6 months)
        'monthly_trends': get_monthly_trends(6),
    }
    
    return analytics


def get_monthly_trends(months=6):
    """Get donation trends for the last N months"""
    from .models import BloodDonation
    
    trends = []
    today = timezone.now().date()
    
    for i in range(months):
        month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        donations = BloodDonation.objects.filter(
            donation_date__gte=month_start,
            donation_date__lte=month_end,
            status='approved'
        )
        
        trends.append({
            'month': month_start.strftime('%B %Y'),
            'donations': donations.count(),
            'units': donations.aggregate(total=Sum('units_donated'))['total'] or 0
        })
    
    return list(reversed(trends))


# ============================================
# 5. QR CODE SYSTEM
# ============================================

def generate_qr_code(qr_type, related_object, data=None):
    """Generate QR code for donors, certificates, or blood bags"""
    from .models import QRCode
    
    # Generate unique code
    code = f"{qr_type.upper()}-{uuid.uuid4().hex[:12].upper()}"
    
    # Prepare data
    qr_data = {
        'code': code,
        'type': qr_type,
        'generated_at': timezone.now().isoformat(),
    }
    
    if data:
        qr_data.update(data)
    
    # Create QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Create QRCode record
    qr_code = QRCode.objects.create(
        qr_type=qr_type,
        code=code,
        data=qr_data
    )
    
    # Save image
    qr_code.qr_image.save(f'{code}.png', File(buffer), save=True)
    
    # Link to related object
    if qr_type == 'donor' and hasattr(related_object, 'qr_codes'):
        qr_code.donor = related_object
    elif qr_type == 'certificate' and hasattr(related_object, 'qr_codes'):
        qr_code.donation = related_object
    elif qr_type == 'appointment' and hasattr(related_object, 'qr_codes'):
        qr_code.appointment = related_object
    
    qr_code.save()
    
    return qr_code


def verify_qr_code(code):
    """Verify and retrieve QR code information"""
    from .models import QRCode
    
    try:
        qr_code = QRCode.objects.get(code=code)
        qr_code.scanned_count += 1
        qr_code.last_scanned = timezone.now()
        qr_code.save()
        
        return {
            'valid': True,
            'qr_code': qr_code,
            'data': qr_code.data
        }
    except QRCode.DoesNotExist:
        return {
            'valid': False,
            'error': 'Invalid QR code'
        }
