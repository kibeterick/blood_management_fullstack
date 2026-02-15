"""
Advanced Analytics for Blood Management System
"""
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Donor, BloodRequest, BloodDonation, BloodInventory


def get_dashboard_analytics():
    """
    Get comprehensive analytics for admin dashboard
    """
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    analytics = {
        # Overall Statistics
        'total_donors': Donor.objects.count(),
        'active_donors': Donor.objects.filter(is_available=True).count(),
        'total_requests': BloodRequest.objects.count(),
        'total_donations': BloodDonation.objects.count(),
        
        # Recent Activity (Last 30 days)
        'new_donors_30d': Donor.objects.filter(created_at__gte=last_30_days).count(),
        'new_requests_30d': BloodRequest.objects.filter(created_at__gte=last_30_days).count(),
        'donations_30d': BloodDonation.objects.filter(donation_date__gte=last_30_days.date()).count(),
        
        # Request Status Breakdown
        'pending_requests': BloodRequest.objects.filter(status='pending').count(),
        'approved_requests': BloodRequest.objects.filter(status='approved').count(),
        'fulfilled_requests': BloodRequest.objects.filter(status='fulfilled').count(),
        'cancelled_requests': BloodRequest.objects.filter(status='cancelled').count(),
        
        # Urgency Breakdown
        'critical_requests': BloodRequest.objects.filter(urgency='critical', status='pending').count(),
        'high_urgency_requests': BloodRequest.objects.filter(urgency='high', status='pending').count(),
        
        # Blood Type Distribution
        'donors_by_blood_type': list(
            Donor.objects.values('blood_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        ),
        
        'requests_by_blood_type': list(
            BloodRequest.objects.values('blood_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        ),
        
        # Donation Statistics
        'total_units_donated': BloodDonation.objects.aggregate(
            total=Sum('units_donated')
        )['total'] or 0,
        
        'avg_units_per_donation': BloodDonation.objects.aggregate(
            avg=Avg('units_donated')
        )['avg'] or 0,
        
        # Inventory Status
        'low_stock_count': BloodInventory.objects.filter(
            units_available__lt=F('minimum_threshold')
        ).count() if BloodInventory.objects.exists() else 0,
        
        # Top Donors (by donation count)
        'top_donors': list(
            Donor.objects.annotate(
                donation_count=Count('donations')
            ).filter(donation_count__gt=0)
            .order_by('-donation_count')[:5]
        ),
        
        # Recent Trends
        'requests_trend': get_requests_trend(days=30),
        'donations_trend': get_donations_trend(days=30),
    }
    
    return analytics


def get_requests_trend(days=30):
    """
    Get blood request trend for the last N days
    """
    from django.db.models.functions import TruncDate
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    trend = list(
        BloodRequest.objects
        .filter(created_at__gte=start_date)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    return trend


def get_donations_trend(days=30):
    """
    Get blood donation trend for the last N days
    """
    from django.db.models.functions import TruncDate
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    trend = list(
        BloodDonation.objects
        .filter(donation_date__gte=start_date)
        .values('donation_date')
        .annotate(count=Count('id'), units=Sum('units_donated'))
        .order_by('donation_date')
    )
    
    return trend


def get_blood_type_compatibility_stats():
    """
    Get statistics on blood type compatibility and availability
    """
    from .utils import get_compatible_blood_types
    
    stats = {}
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    for blood_type in blood_types:
        compatible_donors = get_compatible_blood_types(blood_type, 'receive')
        
        stats[blood_type] = {
            'available_donors': Donor.objects.filter(
                blood_type=blood_type,
                is_available=True
            ).count(),
            'total_donors': Donor.objects.filter(blood_type=blood_type).count(),
            'pending_requests': BloodRequest.objects.filter(
                blood_type=blood_type,
                status='pending'
            ).count(),
            'compatible_donor_types': compatible_donors,
            'total_compatible_donors': Donor.objects.filter(
                blood_type__in=compatible_donors,
                is_available=True
            ).count(),
        }
    
    return stats


def get_donor_engagement_metrics():
    """
    Calculate donor engagement and retention metrics
    """
    from django.db.models import Count, Max
    
    total_donors = Donor.objects.count()
    
    # Donors who have donated at least once
    active_donors = Donor.objects.annotate(
        donation_count=Count('donations')
    ).filter(donation_count__gt=0).count()
    
    # Donors who donated in last 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    recent_donors = Donor.objects.filter(
        last_donation_date__gte=six_months_ago.date()
    ).count()
    
    # Repeat donors (donated more than once)
    repeat_donors = Donor.objects.annotate(
        donation_count=Count('donations')
    ).filter(donation_count__gt=1).count()
    
    metrics = {
        'total_registered': total_donors,
        'active_donors': active_donors,
        'recent_donors': recent_donors,
        'repeat_donors': repeat_donors,
        'engagement_rate': (active_donors / total_donors * 100) if total_donors > 0 else 0,
        'retention_rate': (recent_donors / active_donors * 100) if active_donors > 0 else 0,
        'repeat_rate': (repeat_donors / active_donors * 100) if active_donors > 0 else 0,
    }
    
    return metrics


def get_request_fulfillment_metrics():
    """
    Calculate blood request fulfillment metrics
    """
    total_requests = BloodRequest.objects.count()
    fulfilled = BloodRequest.objects.filter(status='fulfilled').count()
    pending = BloodRequest.objects.filter(status='pending').count()
    cancelled = BloodRequest.objects.filter(status='cancelled').count()
    
    # Average time to fulfill (for fulfilled requests)
    fulfilled_requests = BloodRequest.objects.filter(
        status='fulfilled',
        fulfilled_date__isnull=False
    )
    
    avg_fulfillment_time = None
    if fulfilled_requests.exists():
        total_time = sum([
            (req.fulfilled_date - req.created_at).days
            for req in fulfilled_requests
        ])
        avg_fulfillment_time = total_time / fulfilled_requests.count()
    
    metrics = {
        'total_requests': total_requests,
        'fulfilled_count': fulfilled,
        'pending_count': pending,
        'cancelled_count': cancelled,
        'fulfillment_rate': (fulfilled / total_requests * 100) if total_requests > 0 else 0,
        'avg_fulfillment_days': round(avg_fulfillment_time, 1) if avg_fulfillment_time else None,
    }
    
    return metrics


# Import F for the low_stock_count query
from django.db.models import F
