"""
API Views for AJAX requests and mobile app integration
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Donor, BloodRequest, BloodInventory
from .utils import check_donor_eligibility, get_compatible_blood_types
import json


@login_required
@require_http_methods(["GET"])
def donor_search_api(request):
    """
    AJAX endpoint for real-time donor search
    """
    query = request.GET.get('q', '')
    blood_type = request.GET.get('blood_type', '')
    availability = request.GET.get('availability', '')
    city = request.GET.get('city', '')

    donors = Donor.objects.all()

    # Apply filters
    if query:
        donors = donors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )

    if blood_type:
        donors = donors.filter(blood_type=blood_type)

    if availability == 'available':
        donors = donors.filter(is_available=True)
    elif availability == 'unavailable':
        donors = donors.filter(is_available=False)

    if city:
        donors = donors.filter(city__icontains=city)

    # Serialize data
    data = [{
        'id': donor.id,
        'first_name': donor.first_name,
        'last_name': donor.last_name,
        'blood_type': donor.blood_type,
        'email': donor.email,
        'phone_number': donor.phone_number,
        'city': donor.city,
        'state': donor.state,
        'is_available': donor.is_available,
        'last_donation_date': donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else None,
    } for donor in donors[:50]]  # Limit to 50 results

    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["GET"])
def check_donor_eligibility_api(request, donor_id):
    """
    Check if a donor is eligible to donate
    """
    try:
        donor = Donor.objects.get(id=donor_id)
        is_eligible, message = check_donor_eligibility(donor)
        
        return JsonResponse({
            'eligible': is_eligible,
            'message': message,
            'donor_name': f"{donor.first_name} {donor.last_name}",
            'blood_type': donor.blood_type,
        })
    except Donor.DoesNotExist:
        return JsonResponse({'error': 'Donor not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def blood_inventory_api(request):
    """
    Get current blood inventory status
    """
    inventory = BloodInventory.objects.all()
    
    data = [{
        'blood_type': item.blood_type,
        'units_available': item.units_available,
        'minimum_threshold': item.minimum_threshold,
        'is_low_stock': item.is_low_stock(),
        'last_updated': item.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
    } for item in inventory]
    
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["GET"])
def compatible_donors_api(request):
    """
    Find compatible donors for a specific blood type
    """
    blood_type = request.GET.get('blood_type', '')
    
    if not blood_type:
        return JsonResponse({'error': 'Blood type is required'}, status=400)
    
    # Get compatible blood types
    compatible_types = get_compatible_blood_types(blood_type, 'receive')
    
    # Find available donors with compatible blood types
    donors = Donor.objects.filter(
        blood_type__in=compatible_types,
        is_available=True
    )
    
    data = {
        'requested_blood_type': blood_type,
        'compatible_types': compatible_types,
        'available_donors': [{
            'id': donor.id,
            'name': f"{donor.first_name} {donor.last_name}",
            'blood_type': donor.blood_type,
            'phone': donor.phone_number,
            'city': donor.city,
        } for donor in donors]
    }
    
    return JsonResponse(data)


@login_required
@require_http_methods(["GET"])
def request_statistics_api(request):
    """
    Get blood request statistics
    """
    from django.db.models import Count
    
    stats = {
        'by_status': list(
            BloodRequest.objects.values('status')
            .annotate(count=Count('id'))
        ),
        'by_urgency': list(
            BloodRequest.objects.values('urgency')
            .annotate(count=Count('id'))
        ),
        'by_blood_type': list(
            BloodRequest.objects.values('blood_type')
            .annotate(count=Count('id'))
        ),
        'total': BloodRequest.objects.count(),
        'pending': BloodRequest.objects.filter(status='pending').count(),
        'critical': BloodRequest.objects.filter(urgency='critical', status='pending').count(),
    }
    
    return JsonResponse(stats)


@login_required
@require_http_methods(["POST"])
def update_donor_availability_api(request, donor_id):
    """
    Update donor availability status
    """
    try:
        donor = Donor.objects.get(id=donor_id)
        data = json.loads(request.body)
        
        donor.is_available = data.get('is_available', donor.is_available)
        donor.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Donor availability updated',
            'is_available': donor.is_available
        })
    except Donor.DoesNotExist:
        return JsonResponse({'error': 'Donor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def dashboard_stats_api(request):
    """
    Get dashboard statistics for charts
    """
    from .analytics import get_dashboard_analytics
    
    analytics = get_dashboard_analytics()
    
    return JsonResponse(analytics, safe=False)
