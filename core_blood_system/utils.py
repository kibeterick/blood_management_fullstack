"""
Utility functions for Blood Management System
"""
from datetime import datetime, timedelta
from django.utils import timezone


def check_donor_eligibility(donor):
    """
    Check if a donor is eligible to donate blood
    Rules:
    - Must wait 56 days (8 weeks) between whole blood donations
    - Must be marked as available
    """
    if not donor.is_available:
        return False, "Donor is currently marked as unavailable"
    
    if donor.last_donation_date:
        days_since_last_donation = (timezone.now().date() - donor.last_donation_date).days
        minimum_wait_days = 56  # 8 weeks
        
        if days_since_last_donation < minimum_wait_days:
            days_remaining = minimum_wait_days - days_since_last_donation
            return False, f"Must wait {days_remaining} more days before next donation"
    
    return True, "Eligible to donate"


def get_next_eligible_date(donor):
    """
    Calculate the next date when donor will be eligible
    """
    if not donor.last_donation_date:
        return timezone.now().date()
    
    next_date = donor.last_donation_date + timedelta(days=56)
    return next_date


def get_compatible_blood_types(blood_type, donation_type='receive'):
    """
    Get compatible blood types for donation or receiving
    
    Args:
        blood_type: The blood type to check (e.g., 'A+', 'O-')
        donation_type: 'receive' or 'donate'
    
    Returns:
        List of compatible blood types
    """
    compatibility_matrix = {
        'A+': {
            'can_receive_from': ['A+', 'A-', 'O+', 'O-'],
            'can_donate_to': ['A+', 'AB+']
        },
        'A-': {
            'can_receive_from': ['A-', 'O-'],
            'can_donate_to': ['A+', 'A-', 'AB+', 'AB-']
        },
        'B+': {
            'can_receive_from': ['B+', 'B-', 'O+', 'O-'],
            'can_donate_to': ['B+', 'AB+']
        },
        'B-': {
            'can_receive_from': ['B-', 'O-'],
            'can_donate_to': ['B+', 'B-', 'AB+', 'AB-']
        },
        'AB+': {
            'can_receive_from': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'can_donate_to': ['AB+']
        },
        'AB-': {
            'can_receive_from': ['A-', 'B-', 'AB-', 'O-'],
            'can_donate_to': ['AB+', 'AB-']
        },
        'O+': {
            'can_receive_from': ['O+', 'O-'],
            'can_donate_to': ['A+', 'B+', 'AB+', 'O+']
        },
        'O-': {
            'can_receive_from': ['O-'],
            'can_donate_to': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        }
    }
    
    if blood_type not in compatibility_matrix:
        return []
    
    if donation_type == 'receive':
        return compatibility_matrix[blood_type]['can_receive_from']
    else:
        return compatibility_matrix[blood_type]['can_donate_to']


def calculate_blood_request_priority(blood_request):
    """
    Calculate priority score for blood requests
    Higher score = higher priority
    """
    priority_score = 0
    
    # Urgency scoring
    urgency_scores = {
        'critical': 100,
        'high': 75,
        'medium': 50,
        'low': 25
    }
    priority_score += urgency_scores.get(blood_request.urgency, 0)
    
    # Time-based scoring (older requests get higher priority)
    days_old = (timezone.now() - blood_request.created_at).days
    priority_score += min(days_old * 5, 50)  # Max 50 points for age
    
    # Units needed (more units = slightly higher priority)
    priority_score += min(blood_request.units_needed * 2, 20)  # Max 20 points
    
    return priority_score


def get_blood_statistics():
    """
    Get comprehensive blood donation statistics
    """
    from .models import Donor, BloodRequest, BloodDonation, BloodInventory
    from django.db.models import Count, Sum
    
    stats = {
        'total_donors': Donor.objects.count(),
        'available_donors': Donor.objects.filter(is_available=True).count(),
        'total_requests': BloodRequest.objects.count(),
        'pending_requests': BloodRequest.objects.filter(status='pending').count(),
        'fulfilled_requests': BloodRequest.objects.filter(status='fulfilled').count(),
        'total_donations': BloodDonation.objects.count(),
        'total_units_donated': BloodDonation.objects.aggregate(Sum('units_donated'))['units_donated__sum'] or 0,
        'donors_by_blood_type': Donor.objects.values('blood_type').annotate(count=Count('id')),
        'requests_by_urgency': BloodRequest.objects.values('urgency').annotate(count=Count('id')),
        'low_stock_items': BloodInventory.objects.filter(units_available__lt=5).count(),
    }
    
    return stats


def format_phone_number(phone):
    """
    Format phone number for display
    """
    # Remove all non-numeric characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format as (XXX) XXX-XXXX if 10 digits
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    return phone


def validate_blood_type(blood_type):
    """
    Validate if blood type is valid
    """
    valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_type in valid_types


def get_donation_history_summary(donor):
    """
    Get summary of donor's donation history
    """
    from .models import BloodDonation
    
    donations = BloodDonation.objects.filter(donor=donor).order_by('-donation_date')
    
    summary = {
        'total_donations': donations.count(),
        'total_units': donations.aggregate(Sum('units_donated'))['units_donated__sum'] or 0,
        'last_donation': donations.first().donation_date if donations.exists() else None,
        'recent_donations': donations[:5],  # Last 5 donations
    }
    
    return summary
