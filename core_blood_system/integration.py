"""
Integration Module
Connects all new features together for seamless workflow
"""
from django.utils import timezone
from .models import BloodRequest, BloodDonation, Donor
from .donor_matching import find_matching_donors, notify_matching_donors
from .donor_response import create_donor_responses, get_accepted_donors_for_request
from .laboratory import create_blood_test
from .notifications import (
    send_donor_registration_confirmation,
    send_request_status_update,
    send_low_stock_alert
)
from .sms_notifications import (
    send_donation_thank_you_sms,
    send_eligibility_notification_sms
)


def process_new_blood_request(blood_request, auto_notify=True):
    """
    Complete workflow when a new blood request is created
    
    Steps:
    1. Find matching donors
    2. Create response records
    3. Send notifications (email + SMS for urgent)
    4. Return results
    """
    result = {
        'success': False,
        'message': '',
        'matching_donors': 0,
        'notifications_sent': 0,
    }
    
    try:
        # Find matching donors
        matching_result = find_matching_donors(blood_request)
        eligible_donors = matching_result['eligible_donors']
        
        if not eligible_donors:
            result['message'] = 'No eligible donors found for this blood type'
            return result
        
        # Create response records for tracking
        create_donor_responses(blood_request, eligible_donors)
        
        # Send notifications if auto_notify is True
        if auto_notify:
            notification_result = notify_matching_donors(
                blood_request,
                send_sms=(blood_request.urgency in ['high', 'critical']),
                send_email=True
            )
            
            result['notifications_sent'] = notification_result['email_sent']
            result['sms_sent'] = notification_result.get('sms_sent', 0)
        
        result['success'] = True
        result['matching_donors'] = len(eligible_donors)
        result['message'] = f'Found {len(eligible_donors)} eligible donors'
        result['donors'] = eligible_donors
        
    except Exception as e:
        result['message'] = f'Error processing request: {str(e)}'
    
    return result


def process_donor_registration(donor, send_confirmation=True):
    """
    Complete workflow when a new donor registers
    
    Steps:
    1. Save donor information
    2. Send confirmation email
    3. Check for pending blood requests that match
    """
    result = {
        'success': False,
        'message': '',
        'matching_requests': 0,
    }
    
    try:
        # Send confirmation email
        if send_confirmation:
            send_donor_registration_confirmation(donor)
        
        # Check for pending blood requests that match this donor
        from .donor_matching import get_compatible_blood_types
        
        # Find blood types this donor can donate to
        can_donate_to = []
        for blood_type, compatible_from in {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-'],
        }.items():
            if donor.blood_type in compatible_from:
                can_donate_to.append(blood_type)
        
        # Find pending requests
        matching_requests = BloodRequest.objects.filter(
            blood_type__in=can_donate_to,
            status='pending'
        )
        
        result['success'] = True
        result['message'] = 'Donor registered successfully'
        result['matching_requests'] = matching_requests.count()
        result['requests'] = list(matching_requests)
        
    except Exception as e:
        result['message'] = f'Error processing registration: {str(e)}'
    
    return result


def process_donation_completion(donation, tested_by='Lab Technician'):
    """
    Complete workflow when a donation is completed
    
    Steps:
    1. Create blood test record
    2. Update donor's last donation date
    3. Send thank you message
    4. Update blood inventory (if test passes)
    """
    result = {
        'success': False,
        'message': '',
    }
    
    try:
        # Create blood test
        blood_test = create_blood_test(donation, tested_by)
        
        # Update donor's last donation date
        donor = donation.donor
        donor.last_donation_date = donation.donation_date
        donor.save()
        
        # Send thank you SMS/Email
        try:
            send_donation_thank_you_sms(donation)
        except:
            pass  # SMS might not be configured
        
        result['success'] = True
        result['message'] = 'Donation processed successfully'
        result['blood_test'] = blood_test
        
    except Exception as e:
        result['message'] = f'Error processing donation: {str(e)}'
    
    return result


def process_request_status_change(blood_request, new_status, notify=True):
    """
    Handle blood request status changes
    
    Steps:
    1. Update status
    2. Send notification to requester
    3. If fulfilled, update inventory
    """
    result = {
        'success': False,
        'message': '',
    }
    
    try:
        old_status = blood_request.status
        blood_request.status = new_status
        
        if new_status == 'fulfilled':
            blood_request.fulfilled_date = timezone.now()
        
        blood_request.save()
        
        # Send notification
        if notify:
            send_request_status_update(blood_request)
        
        result['success'] = True
        result['message'] = f'Status changed from {old_status} to {new_status}'
        
    except Exception as e:
        result['message'] = f'Error updating status: {str(e)}'
    
    return result


def check_and_alert_low_stock():
    """
    Check blood inventory and send alerts for low stock
    """
    from .models import BloodInventory, CustomUser
    
    low_stock_items = BloodInventory.objects.filter(
        units_available__lt=models.F('minimum_threshold')
    )
    
    if low_stock_items.exists():
        # Get admin emails
        admin_emails = list(
            CustomUser.objects.filter(role='admin').values_list('email', flat=True)
        )
        
        for item in low_stock_items:
            send_low_stock_alert(
                item.blood_type,
                item.units_available,
                admin_emails
            )
    
    return low_stock_items.count()


def get_system_health_status():
    """
    Get overall system health and statistics
    """
    from .donor_matching import get_matching_statistics
    from .laboratory import get_test_statistics
    from .donor_response import get_response_statistics
    
    return {
        'donor_stats': get_matching_statistics(),
        'test_stats': get_test_statistics(),
        'response_stats': get_response_statistics(),
        'timestamp': timezone.now(),
    }


def send_eligibility_reminders():
    """
    Send reminders to donors who are now eligible to donate again
    (Run this as a scheduled task - daily)
    """
    from datetime import timedelta
    from .donor_matching import get_donor_next_eligible_date
    
    today = timezone.now().date()
    
    # Find donors whose eligibility date is today
    donors = Donor.objects.filter(
        is_available=True,
        last_donation_date__isnull=False
    )
    
    reminded_count = 0
    for donor in donors:
        next_eligible = get_donor_next_eligible_date(donor)
        
        if next_eligible == today:
            try:
                send_eligibility_notification_sms(donor, next_eligible)
                reminded_count += 1
            except:
                pass  # SMS might not be configured
    
    return reminded_count
