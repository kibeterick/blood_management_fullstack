"""
Advanced Security Features - Phase 2
Implements: 2FA, Email Verification, Activity Logs, Session Management
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import pyotp
import qrcode
from io import BytesIO
import base64
from datetime import timedelta
import secrets
import hashlib

User = get_user_model()


# ==========================================
# TWO-FACTOR AUTHENTICATION (2FA)
# ==========================================

class TwoFactorAuth(models.Model):
    """Store 2FA secrets for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor')
    secret_key = models.CharField(max_length=32, unique=True)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.TextField(blank=True)  # Comma-separated backup codes
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'two_factor_auth'
        verbose_name = 'Two-Factor Authentication'
        verbose_name_plural = 'Two-Factor Authentications'
    
    def __str__(self):
        return f'2FA for {self.user.username}'
    
    @classmethod
    def generate_secret(cls, user):
        """Generate a new 2FA secret for user"""
        secret = pyotp.random_base32()
        two_factor, created = cls.objects.get_or_create(
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
    
    def get_totp(self):
        """Get TOTP object for generating/verifying codes"""
        return pyotp.TOTP(self.secret_key)
    
    def verify_token(self, token):
        """Verify a 2FA token"""
        totp = self.get_totp()
        
        # Check if it's a valid TOTP code
        if totp.verify(token, valid_window=1):
            self.last_used = timezone.now()
            self.save()
            return True
        
        # Check if it's a backup code
        if self.backup_codes:
            codes = self.backup_codes.split(',')
            if token.upper() in codes:
                # Remove used backup code
                codes.remove(token.upper())
                self.backup_codes = ','.join(codes)
                self.last_used = timezone.now()
                self.save()
                return True
        
        return False
    
    def get_qr_code(self):
        """Generate QR code for 2FA setup"""
        totp = self.get_totp()
        provisioning_uri = totp.provisioning_uri(
            name=self.user.email,
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
    
    def get_backup_codes_list(self):
        """Get list of backup codes"""
        if self.backup_codes:
            return self.backup_codes.split(',')
        return []


# ==========================================
# EMAIL VERIFICATION
# ==========================================

class EmailVerification(models.Model):
    """Email verification tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Email verification for {self.user.username}'
    
    @classmethod
    def create_token(cls, user):
        """Create a new verification token"""
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        verification = cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return verification
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def send_verification_email(self, request):
        """Send verification email to user"""
        verification_url = request.build_absolute_uri(
            f'/verify-email/{self.token}/'
        )
        
        subject = 'Verify Your Email - Blood Management System'
        message = f"""
        Hello {self.user.first_name or self.user.username},
        
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
            [self.user.email],
            fail_silently=False,
        )


# ==========================================
# USER ACTIVITY LOGS
# ==========================================

class UserActivityLog(models.Model):
    """Track user activities for security and audit purposes"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('email_verified', 'Email Verified'),
        ('failed_login', 'Failed Login'),
        ('session_terminated', 'Session Terminated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)  # City, Country
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    details = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.action} at {self.timestamp}'
    
    @classmethod
    def log_activity(cls, user, action, request, success=True, details=''):
        """Log a user activity"""
        from core_blood_system.security import get_client_ip
        
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Parse device info from user agent
        device_info = cls._parse_device_info(user_agent)
        
        return cls.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            success=success,
            details=details
        )
    
    @staticmethod
    def _parse_device_info(user_agent):
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
# USER SESSIONS MANAGEMENT
# ==========================================

class UserSession(models.Model):
    """Track active user sessions for security"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f'{self.user.username} - {self.device_info}'
    
    @classmethod
    def create_session(cls, user, request):
        """Create or update a session"""
        from core_blood_system.security import get_client_ip
        
        session_key = request.session.session_key
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        device_info = UserActivityLog._parse_device_info(user_agent)
        
        session, created = cls.objects.update_or_create(
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
    
    @classmethod
    def terminate_session(cls, session_key):
        """Terminate a specific session"""
        try:
            session = cls.objects.get(session_key=session_key)
            session.is_active = False
            session.save()
            
            # Delete Django session
            from django.contrib.sessions.models import Session
            Session.objects.filter(session_key=session_key).delete()
            
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def terminate_all_except_current(cls, user, current_session_key):
        """Terminate all sessions except the current one"""
        sessions = cls.objects.filter(user=user, is_active=True).exclude(
            session_key=current_session_key
        )
        
        from django.contrib.sessions.models import Session
        for session in sessions:
            session.is_active = False
            session.save()
            Session.objects.filter(session_key=session.session_key).delete()
        
        return sessions.count()


# ==========================================
# ADMIN AUDIT TRAIL
# ==========================================

class AdminAuditLog(models.Model):
    """Immutable audit log for admin actions"""
    
    admin_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='admin_actions')
    action_type = models.CharField(max_length=50)  # create, update, delete, approve, reject
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(default=dict)  # Store what changed
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'admin_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f'{self.admin_user.username} - {self.action_type} {self.model_name} #{self.object_id}'
    
    @classmethod
    def log_action(cls, admin_user, action_type, obj, request, changes=None, reason=''):
        """Log an admin action"""
        from core_blood_system.security import get_client_ip
        
        return cls.objects.create(
            admin_user=admin_user,
            action_type=action_type,
            model_name=obj.__class__.__name__,
            object_id=obj.pk,
            object_repr=str(obj),
            changes=changes or {},
            ip_address=get_client_ip(request),
            reason=reason
        )
