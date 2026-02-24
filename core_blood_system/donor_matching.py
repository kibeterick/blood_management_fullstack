"""
Automated Donor Matching System
Matches blood requests with eligible donors based on multiple criteria
"""
from datetime import datetime, timedelta
from django.db.models import Q
from .models import Donor, BloodRequest, BLOOD_TYPE_CHOICES
from .notifications import send_blood_request_notification
from .sms_notifications import send_urgent_blood_request_sms


# Blood compatibility matrix
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-'],  # Universal donor
}


def get_compatible_blood_types(recipient_blood_type):
    """
    Get list of blood types that can donate to the recipient
    """
    return BLOOD_COMPATIBILITY.get(recipient_blood_type, [])


def check_donor_eligibility(donor):
    """
    Check if donor is eligible to donate blood
    
    Eligibility criteria:
    - Must be available
    - Must wait at least 56 days (8 weeks) since last donation
    - Age between 18-65 years (if date_of_birth available)
    """
    # Check availability
    if not donor.is_available:
        return False, "Donor marked as unavailable"
    
    # Check last donation date (56-day rule)
    if donor.last_donation_date:
        days_since_donation = (datetime.now().date() - donor.last_donation_date).days
        if days_since_donation < 56:
            days_remaining = 56 - days_since_donation
            return False, f"Must wait {days_remaining} more days since last donation"
    
    # Check age eligibility (if date_of_birth is available)
    if donor.date_of_birth:
        age = (datetime.now().date() - donor.date_of_birth).days // 365
        if age < 18:
            return False, "Donor must be at least 18 years old"
        if age > 65:
            return False, "Donor must be under 65 years old"
    
    return True, "Eligible"


def calculate_distance_score(donor, blood_request):
    """
    Calculate proximity score between donor and hospital
    Higher score = closer proximity
    
    For now, simple city/state matching
    In production, use geolocation APIs
    """
    score = 0
    
    # Extract city from hospital address if possible
    hospital_address_lower = blood_request.hospital_address.lower()
    donor_city_lower = donor.city.lower()
    donor_state_lower = donor.state.lower()
    
    # Same city = highest priority
    if donor_city_lower in hospital_address_lower:
        score += 100
    
    # Same state = medium priority
    if donor_state_lower in hospital_address_lower:
        score += 50
    
    return score


def find_matching_donors(blood_request, max_donors=50):
    """
    Find eligible donors for a blood request
    
    Returns:
        dict with 'eligible_donors', 'ineligible_donors', and 'reasons'
    """
    # Get compatible blood types
    compatible_types = get_compatible_blood_types(blood_request.blood_type)
    
    # Find donors with compatible blood types
    potential_donors = Donor.objects.filter(
        blood_type__in=compatible_types
    ).order_by('-last_donation_date')  # Prioritize those who haven't donated recently
    
    eligible_donors = []
    ineligible_donors = []
    
    for donor in potential_donors:
        is_eligible, reason = check_donor_eligibility(donor)
        
        if is_eligible:
            # Calculate proximity score
            proximity_score = calculate_distance_score(donor, blood_request)
            
            eligible_donors.append({
                'donor': donor,
                'proximity_score': proximity_score,
                'exact_match': donor.blood_type == blood_request.blood_type,
            })
        else:
            ineligible_donors.append({
                'donor': donor,
                'reason': reason,
            })
    
    # Sort eligible donors by:
    # 1. Exact blood type match
    # 2. Proximity score
    # 3. Last donation date (older = higher priority)
    eligible_donors.sort(
        key=lambda x: (
            x['exact_match'],
            x['proximity_score'],
            x['donor'].last_donation_date or datetime.min.date()
        ),
        reverse=True
    )
    
    # Limit to max_donors
    eligible_donors = eligible_donors[:max_donors]
    
    return {
        'eligible_donors': [item['donor'] for item in eligible_donors],
        'eligible_count': len(eligible_donors),
        'ineligible_donors': ineligible_donors,
        'ineligible_count': len(ineligible_donors),
        'compatible_blood_types': compatible_types,
    }


def notify_matching_donors(blood_request, send_sms=True, send_email=True):
    """
    Find and notify all matching donors for a blood request
    
    Returns:
        dict with notification statistics
    """
    # Find matching donors
    matching_result = find_matching_donors(blood_request)
    eligible_donors = matching_result['eligible_donors']
    
    if not eligible_donors:
        return {
            'success': False,
            'message': 'No eligible donors found',
            'eligible_count': 0,
            'email_sent': 0,
            'sms_sent': 0,
        }
    
    # Send email notifications
    email_sent = 0
    if send_email:
        try:
            send_blood_request_notification(blood_request, eligible_donors)
            email_sent = len(eligible_donors)
        except Exception as e:
            print(f"Email notification failed: {str(e)}")
    
    # Send SMS notifications (only for urgent/critical requests)
    sms_sent = 0
    if send_sms and blood_request.urgency in ['high', 'critical']:
        try:
            sms_sent = send_urgent_blood_request_sms(blood_request, eligible_donors)
        except Exception as e:
            print(f"SMS notification failed: {str(e)}")
    
    return {
        'success': True,
        'message': f'Notified {len(eligible_donors)} eligible donors',
        'eligible_count': len(eligible_donors),
        'email_sent': email_sent,
        'sms_sent': sms_sent,
        'donors': eligible_donors,
    }


def get_donor_next_eligible_date(donor):
    """
    Calculate when a donor will be eligible to donate again
    """
    if not donor.last_donation_date:
        return datetime.now().date()  # Eligible now
    
    next_eligible = donor.last_donation_date + timedelta(days=56)
    return next_eligible


def get_eligible_donors_for_blood_type(blood_type, location=None):
    """
    Get all currently eligible donors for a specific blood type
    Optionally filter by location
    """
    compatible_types = get_compatible_blood_types(blood_type)
    
    donors = Donor.objects.filter(
        blood_type__in=compatible_types,
        is_available=True
    )
    
    if location:
        donors = donors.filter(
            Q(city__icontains=location) | Q(state__icontains=location)
        )
    
    eligible_donors = []
    for donor in donors:
        is_eligible, reason = check_donor_eligibility(donor)
        if is_eligible:
            eligible_donors.append(donor)
    
    return eligible_donors


def resend_notifications_to_donors(blood_request):
    """
    Resend notifications to eligible donors
    Used by administrators to remind donors
    """
    return notify_matching_donors(blood_request, send_sms=True, send_email=True)


# Statistics and reporting
def get_matching_statistics():
    """
    Get statistics about donor matching system
    """
    from .models import Donor, BloodRequest
    
    total_donors = Donor.objects.count()
    available_donors = Donor.objects.filter(is_available=True).count()
    
    # Count eligible donors (those who can donate now)
    eligible_count = 0
    for donor in Donor.objects.filter(is_available=True):
        is_eligible, _ = check_donor_eligibility(donor)
        if is_eligible:
            eligible_count += 1
    
    # Blood type distribution
    blood_type_stats = {}
    for blood_type, _ in BLOOD_TYPE_CHOICES:
        count = Donor.objects.filter(blood_type=blood_type, is_available=True).count()
        blood_type_stats[blood_type] = count
    
    return {
        'total_donors': total_donors,
        'available_donors': available_donors,
        'eligible_donors': eligible_count,
        'blood_type_distribution': blood_type_stats,
    }
