"""
Email and SMS notification system for Blood Management
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_blood_request_notification(blood_request, donors):
    """
    Send email notification to matching donors when a blood request is created
    """
    subject = f'Urgent: Blood Request for {blood_request.blood_type}'
    
    for donor in donors:
        context = {
            'donor': donor,
            'request': blood_request,
        }
        
        # HTML email
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #dc3545;">🩸 Urgent Blood Request</h2>
            <p>Dear {donor.first_name} {donor.last_name},</p>
            
            <p>A patient needs your blood type <strong>{blood_request.blood_type}</strong>.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3>Request Details:</h3>
                <ul>
                    <li><strong>Patient:</strong> {blood_request.patient_name}</li>
                    <li><strong>Blood Type:</strong> {blood_request.blood_type}</li>
                    <li><strong>Units Needed:</strong> {blood_request.units_needed}</li>
                    <li><strong>Purpose:</strong> {blood_request.get_purpose_display()}</li>
                    <li><strong>Urgency:</strong> {blood_request.get_urgency_display()}</li>
                    <li><strong>Hospital:</strong> {blood_request.hospital_name}</li>
                    <li><strong>Contact:</strong> {blood_request.contact_number}</li>
                </ul>
            </div>
            
            <p>If you are available to donate, please contact the hospital immediately.</p>
            
            <p style="color: #6c757d; font-size: 12px; margin-top: 30px;">
                This is an automated message from Blood Management System.<br>
                You received this because you are registered as a {blood_request.blood_type} donor.
            </p>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [donor.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email to {donor.email}: {str(e)}")


def send_request_status_update(blood_request):
    """
    Notify requester when their blood request status changes
    """
    subject = f'Blood Request Update - {blood_request.status.title()}'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #dc3545;">Blood Request Status Update</h2>
        <p>Dear {blood_request.requester.first_name},</p>
        
        <p>Your blood request for <strong>{blood_request.patient_name}</strong> has been updated.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3>Current Status: <span style="color: #198754;">{blood_request.get_status_display()}</span></h3>
            <ul>
                <li><strong>Blood Type:</strong> {blood_request.blood_type}</li>
                <li><strong>Units Needed:</strong> {blood_request.units_needed}</li>
                <li><strong>Hospital:</strong> {blood_request.hospital_name}</li>
            </ul>
        </div>
        
        <p>Thank you for using our Blood Management System.</p>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [blood_request.requester.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def send_donor_registration_confirmation(donor):
    """
    Send confirmation email when a donor registers
    """
    subject = 'Welcome to Blood Management System - Donor Registration Confirmed'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #dc3545;">🩸 Welcome, Blood Donor!</h2>
        <p>Dear {donor.first_name} {donor.last_name},</p>
        
        <p>Thank you for registering as a blood donor. Your generosity can save lives!</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3>Your Donor Profile:</h3>
            <ul>
                <li><strong>Name:</strong> {donor.first_name} {donor.last_name}</li>
                <li><strong>Blood Type:</strong> {donor.blood_type}</li>
                <li><strong>Email:</strong> {donor.email}</li>
                <li><strong>Phone:</strong> {donor.phone_number}</li>
                <li><strong>Location:</strong> {donor.city}, {donor.state}</li>
            </ul>
        </div>
        
        <p>You will receive notifications when someone needs your blood type.</p>
        
        <p style="color: #198754; font-weight: bold;">Thank you for being a hero! 💪</p>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [donor.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def send_low_stock_alert(blood_type, current_units, admin_emails):
    """
    Alert administrators when blood inventory is low
    """
    subject = f'⚠️ Low Blood Stock Alert - {blood_type}'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #ffc107;">⚠️ Low Blood Stock Alert</h2>
        
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
            <h3>Blood Type: {blood_type}</h3>
            <p><strong>Current Units:</strong> {current_units}</p>
            <p style="color: #dc3545;">Stock is below minimum threshold!</p>
        </div>
        
        <p>Please take action to replenish the stock.</p>
        
        <p><strong>Recommended Actions:</strong></p>
        <ul>
            <li>Contact registered {blood_type} donors</li>
            <li>Organize a blood donation drive</li>
            <li>Coordinate with nearby blood banks</li>
        </ul>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send alert: {str(e)}")
