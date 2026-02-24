"""
Donor Response and Confirmation System
Allows donors to accept/decline blood donation requests
"""
from django.db import models
from django.utils import timezone
from .models import Donor, BloodRequest, CustomUser


class DonorResponse(models.Model):
    """
    Track donor responses to blood requests
    """
    RESPONSE_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
    ]
    
    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name='donor_responses'
    )
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    response_status = models.CharField(
        max_length=20,
        choices=RESPONSE_CHOICES,
        default='pending'
    )
    response_date = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    notified_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blood_request', 'donor']
        ordering = ['-notified_at']
    
    def __str__(self):
        return f"{self.donor} - {self.blood_request.patient_name} ({self.response_status})"
    
    def accept_request(self, notes=''):
        """Donor accepts the blood donation request"""
        self.response_status = 'accepted'
        self.response_date = timezone.now()
        self.notes = notes
        self.save()
        
        # Send confirmation email to requester
        from .notifications import send_donor_acceptance_notification
        send_donor_acceptance_notification(self)
        
        return True
    
    def decline_request(self, reason=''):
        """Donor declines the blood donation request"""
        self.response_status = 'declined'
        self.response_date = timezone.now()
        self.decline_reason = reason
        self.save()
        
        return True
    
    def mark_completed(self):
        """Mark donation as completed"""
        self.response_status = 'completed'
        self.save()
        
        return True


def create_donor_responses(blood_request, donors):
    """
    Create response records for all notified donors
    """
    responses = []
    for donor in donors:
        response, created = DonorResponse.objects.get_or_create(
            blood_request=blood_request,
            donor=donor,
            defaults={'response_status': 'pending'}
        )
        responses.append(response)
    
    return responses


def get_pending_requests_for_donor(donor):
    """
    Get all pending blood requests for a specific donor
    """
    return DonorResponse.objects.filter(
        donor=donor,
        response_status='pending',
        blood_request__status='pending'
    ).select_related('blood_request')


def get_donor_response_history(donor):
    """
    Get complete response history for a donor
    """
    return DonorResponse.objects.filter(
        donor=donor
    ).select_related('blood_request').order_by('-notified_at')


def get_request_responses(blood_request):
    """
    Get all donor responses for a specific blood request
    """
    return DonorResponse.objects.filter(
        blood_request=blood_request
    ).select_related('donor').order_by('-response_date')


def get_accepted_donors_for_request(blood_request):
    """
    Get list of donors who accepted a blood request
    """
    responses = DonorResponse.objects.filter(
        blood_request=blood_request,
        response_status='accepted'
    ).select_related('donor')
    
    return [response.donor for response in responses]


def get_response_statistics(blood_request=None):
    """
    Get statistics about donor responses
    """
    if blood_request:
        responses = DonorResponse.objects.filter(blood_request=blood_request)
    else:
        responses = DonorResponse.objects.all()
    
    total = responses.count()
    accepted = responses.filter(response_status='accepted').count()
    declined = responses.filter(response_status='declined').count()
    pending = responses.filter(response_status='pending').count()
    completed = responses.filter(response_status='completed').count()
    
    acceptance_rate = (accepted / total * 100) if total > 0 else 0
    
    return {
        'total_notifications': total,
        'accepted': accepted,
        'declined': declined,
        'pending': pending,
        'completed': completed,
        'acceptance_rate': round(acceptance_rate, 2),
    }
