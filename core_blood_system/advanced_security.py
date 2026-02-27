"""
Advanced Security Features - Phase 2
Helper methods for 2FA, Email Verification, Activity Logs, Session Management

Note: Models are defined in models.py
This file contains only helper methods and business logic.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import pyotp
import qrcode
from io import BytesIO
import base64
import secrets


# ==========================================
# TWO-FACTOR AUTHENTICATION HELPERS
# ==========================================

def generate_2fa_secret(user):
    """Generate a new 2FA secret for user"""
    from core_blood_system.models import TwoFactorAuth
    
    secret = pyotp.random_base32()
    two_factor, created = TwoFactorAuth.objects.get_or_create(
        user=user,
        defaults={'secret_key': secret}
    )
    if not created:
        two_factor.secret_key = secret
        two_factor.save()
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    two_factor.backup_codes = ','.join(backup_codes)
    two_factor.save()
    
    return two_factor


def get_totp(secret_key):
    """Get TOTP object for generating/verifying codes"""
    return pyotp.TOTP(secret_key)


def verify_2fa_token(two_factor, token):
    """Verify a 2FA token"""
    totp = get_totp(two_factor.secret_key)
    
    # Check if it's a valid TOTP code
    if totp.verify(token, valid_window=1):
        two_factor.last_used = timezone.now()
        two_factor.save()
        return True
    
    # Check if it's a backup code
    if two_factor.backup_codes:
        codes = two_factor.backup_codes.split(',')
        if token.upper() in codes:
            # Remove used backup code
            codes.remove(token.upper())
            two_factor.backup_codes = ','.join(codes)
            two_factor.last_used = timezone.now()
            two_factor.save()
            return True
    
    return False


def generate_qr_code(two_factor):
    """Generate QR code for 2FA setup"""
    totp = get_totp(two_factor.secret_key)
    provisioning_uri = totp.provisioning_uri(
        name=two_factor.user.email,
        issuer_name='Blood Management System'
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'


def get_backup_codes_list(two_factor):
    """Get list of backup codes"""
    if two_factor.backup_codes:
        return two_factor.backup_codes.split(',')
    return []


# ==========================================
# EMAIL VERIFICATION HELPERS
# ==========================================

def create_verification_token(user):
    """Create a new verification token"""
    from core_blood_system.models import EmailVerification
    
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=24)
    
    verification = EmailVerification.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    return verification


def is_verification_valid(verification):
    """Check if token is still valid"""
    return not verification.is_used and timezone.now() < verification.expires_at


def send_verification_email(verification, request):
    """Send verification email to user"""
    verification_url = request.build_absolute_uri(
        f'/verify-email/{verification.token}/'
    )
    
    subject = 'Verify Your Email - Blood Management System'
    message = f"""
    Hello {verification.user.first_name or verification.user.username},
    
    Thank you for registering with Blood Management System!
    
    Please verify your email address by clicking the link below:
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    Blood Management System Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [verification.user.email],
        fail_silently=False,
    )


# ==========================================
# USER ACTIVITY LOG HELPERS
# ==========================================

def log_user_activity(user, action, request, success=True, details=''):
    """Log a user activity"""
    from core_blood_system.models import UserActivityLog
    from core_blood_system.security import get_client_ip
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Parse device info from user agent
    device_info = parse_device_info(user_agent)
    
    return UserActivityLog.objects.create(
        user=user,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        device_info=device_info,
        success=success,
        details=details
    )


def parse_device_info(user_agent):
    """Parse device information from user agent string"""
    if not user_agent:
        return 'Unknown Device'
    
    ua_lower = user_agent.lower()
    
    # Detect OS
    if 'windows' in ua_lower:
        os = 'Windows'
    elif 'mac' in ua_lower:
        os = 'macOS'
    elif 'linux' in ua_lower:
        os = 'Linux'
    elif 'android' in ua_lower:
        os = 'Android'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower:
        os = 'iOS'
    else:
        os = 'Unknown OS'
    
    # Detect browser
    if 'chrome' in ua_lower and 'edg' not in ua_lower:
        browser = 'Chrome'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = 'Safari'
    elif 'edg' in ua_lower:
        browser = 'Edge'
    else:
        browser = 'Unknown Browser'
    
    return f'{os} - {browser}'


# ==========================================
# USER SESSION HELPERS
# ==========================================

def create_user_session(user, request):
    """Create or update a session"""
    from core_blood_system.models import UserSession
    from core_blood_system.security import get_client_ip
    
    session_key = request.session.session_key
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device_info = parse_device_info(user_agent)
    
    session, created = UserSession.objects.update_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'device_info': device_info,
            'is_active': True
        }
    )
    return session


def terminate_session(session_key):
    """Terminate a specific session"""
    from core_blood_system.models import UserSession
    from django.contrib.sessions.models import Session
    
    try:
        session = UserSession.objects.get(session_key=session_key)
        session.is_active = False
        session.save()
        
        # Delete Django session
        Session.objects.filter(session_key=session_key).delete()
        
        return True
    except UserSession.DoesNotExist:
        return False


def terminate_all_sessions_except_current(user, current_session_key):
    """Terminate all sessions except the current one"""
    from core_blood_system.models import UserSession
    from django.contrib.sessions.models import Session
    
    sessions = UserSession.objects.filter(user=user, is_active=True).exclude(
        session_key=current_session_key
    )
    
    for session in sessions:
        session.is_active = False
        session.save()
        Session.objects.filter(session_key=session.session_key).delete()
    
    return sessions.count()


# ==========================================
# ADMIN AUDIT LOG HELPERS
# ==========================================

def log_admin_action(admin_user, action_type, obj, request, changes=None, reason=''):
    """Log an admin action"""
    from core_blood_system.models import AdminAuditLog
    from core_blood_system.security import get_client_ip
    
    return AdminAuditLog.objects.create(
        admin_user=admin_user,
        action_type=action_type,
        model_name=obj.__class__.__name__,
        object_id=obj.pk,
        object_repr=str(obj),
        changes=changes or {},
        ip_address=get_client_ip(request),
        reason=reason
    )
