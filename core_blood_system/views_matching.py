"""
Feature 3: Blood Request Matching Algorithm
Views for donor-request matching
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import BloodRequest, MatchedDonor, Donor
from .enhancements import match_donors_to_request, notify_matched_donors


@login_required
def match_results(request, request_id):
    """View matched donors for a blood request"""
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    
    # Check permission
    if request.user.role != 'admin' and blood_request.requester != request.user:
        messages.error(request, 'You do not have permission to view this.')
        return redirect('user_dashboard')
    
    # Get matched donors
    matches = MatchedDonor.objects.filter(blood_request=blood_request).select_related('donor').order_by('-match_score')
    
    context = {
        'blood_request': blood_request,
        'matches': matches,
    }
    
    return render(request, 'matching/match_results.html', context)


@login_required
def trigger_matching(request, request_id):
    """Manually trigger matching for a blood request (Admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can trigger matching.')
        return redirect('user_dashboard')
    
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    
    # Run matching algorithm
    matches = match_donors_to_request(blood_request)
    
    # Notify matched donors
    notify_matched_donors(blood_request)
    
    messages.success(request, f'Found {len(matches)} compatible donors and sent notifications!')
    return redirect('match_results', request_id=request_id)


@login_required
def donor_response(request, match_id):
    """Donor responds to a match (accept/decline)"""
    match = get_object_or_404(MatchedDonor, id=match_id)
    
    # Check permission
    if not hasattr(request.user, 'donor') or match.donor != request.user.donor:
        messages.error(request, 'You do not have permission to respond to this match.')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        response = request.POST.get('response')
        
        if response == 'accept':
            match.status = 'accepted'
            match.responded_at = timezone.now()
            match.save()
            messages.success(request, 'Thank you for accepting! The requester will be notified.')
        elif response == 'decline':
            match.status = 'declined'
            match.responded_at = timezone.now()
            match.save()
            messages.info(request, 'You have declined this request.')
        
        return redirect('my_matches')
    
    context = {
        'match': match,
    }
    
    return render(request, 'matching/donor_response.html', context)


@login_required
def my_matches(request):
    """View all matches for the current donor"""
    try:
        donor = Donor.objects.get(user=request.user)
        matches = MatchedDonor.objects.filter(donor=donor).select_related('blood_request').order_by('-created_at')
    except Donor.DoesNotExist:
        matches = []
    
    context = {
        'matches': matches,
    }
    
    return render(request, 'matching/my_matches.html', context)


@login_required
def admin_matching_dashboard(request):
    """Admin dashboard for viewing all matches (Admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can access this page.')
        return redirect('user_dashboard')
    
    # Get all matches
    matches = MatchedDonor.objects.all().select_related('donor', 'blood_request').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        matches = matches.filter(status=status_filter)
    
    # Statistics
    total_matches = MatchedDonor.objects.count()
    accepted_matches = MatchedDonor.objects.filter(status='accepted').count()
    pending_matches = MatchedDonor.objects.filter(status__in=['matched', 'notified']).count()
    
    context = {
        'matches': matches,
        'status_filter': status_filter,
        'total_matches': total_matches,
        'accepted_matches': accepted_matches,
        'pending_matches': pending_matches,
    }
    
    return render(request, 'matching/admin_matching_dashboard.html', context)
