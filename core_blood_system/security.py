"""
Advanced Security Features for Blood Management System
Protects against common attacks: SQL Injection, XSS, CSRF, Brute Force, etc.
"""

from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from functools import wraps
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ==========================================
# RATE LIMITING - Prevent Brute Force Attacks
# ==========================================

def rate_limit(max_attempts=5, window_minutes=15):
    """
    Rate limiting decorator to prevent brute force attacks
    Usage: @rate_limit(max_attempts=5, window_minutes=15)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get client IP address
            ip_address = get_client_ip(request)
            cache_key = f'rate_limit_{view_func.__name__}_{ip_address}'
            
            # Get current attempt count
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                logger.warning(f'Rate limit exceeded for {ip_address} on {view_func.__name__}')
                return HttpResponseForbidden(
                    f'Too many attempts. Please try again in {window_minutes} minutes.'
                )
            
            # Increment attempts
            cache.set(cache_key, attempts + 1, window_minutes * 60)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def get_client_ip(request):
    """Get the real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==========================================
# LOGIN ATTEMPT TRACKING
# ==========================================

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts"""
    ip_address = get_client_ip(request)
    username = credentials.get('username', 'unknown')
    
    logger.warning(
        f'Failed login attempt - Username: {username}, IP: {ip_address}, '
        f'Time: {datetime.now()}'
    )
    
    # Track failed attempts
    cache_key = f'failed_login_{ip_address}'
    failed_attempts = cache.get(cache_key, 0) + 1
    cache.set(cache_key, failed_attempts, 3600)  # 1 hour
    
    # Block IP after 10 failed attempts
    if failed_attempts >= 10:
        cache.set(f'blocked_ip_{ip_address}', True, 86400)  # 24 hours
        logger.error(f'IP {ip_address} blocked due to excessive failed login attempts')


def check_ip_blocked(request):
    """Check if IP is blocked"""
    ip_address = get_client_ip(request)
    return cache.get(f'blocked_ip_{ip_address}', False)


# ==========================================
# INPUT VALIDATION & SANITIZATION
# ==========================================

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<script>', '</script>', '<iframe>', '</iframe>', 
                      'javascript:', 'onerror=', 'onload=']
    
    text_lower = text.lower()
    for char in dangerous_chars:
        if char in text_lower:
            logger.warning(f'Potential XSS attempt detected: {text}')
            text = text.replace(char, '')
    
    return text


def validate_phone_number(phone):
    """Validate phone number format"""
    import re
    # Kenyan phone number format: +254XXXXXXXXX or 07XXXXXXXX or 01XXXXXXXX
    pattern = r'^(\+254|0)[17]\d{8}$'
    return bool(re.match(pattern, phone))


def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ==========================================
# PERMISSION DECORATORS
# ==========================================

def admin_required(view_func):
    """Decorator to ensure only admins can access a view"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        
        if request.user.role != 'admin':
            logger.warning(
                f'Unauthorized access attempt by {request.user.username} '
                f'to admin-only view: {view_func.__name__}'
            )
            return HttpResponseForbidden('You do not have permission to access this page.')
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def user_or_admin_required(view_func):
    """Decorator to ensure authenticated users can access a view"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


# ==========================================
# AUDIT LOGGING
# ==========================================

def log_user_action(user, action, details=''):
    """Log user actions for audit trail"""
    logger.info(
        f'USER ACTION - User: {user.username}, Role: {user.role}, '
        f'Action: {action}, Details: {details}, Time: {datetime.now()}'
    )


def log_data_modification(user, model_name, action, object_id, details=''):
    """Log data modifications (create, update, delete)"""
    logger.info(
        f'DATA MODIFICATION - User: {user.username}, Model: {model_name}, '
        f'Action: {action}, Object ID: {object_id}, Details: {details}, '
        f'Time: {datetime.now()}'
    )


# ==========================================
# SESSION SECURITY
# ==========================================

def check_session_security(request):
    """Check session security and detect session hijacking"""
    # Check if user agent changed (possible session hijacking)
    session_user_agent = request.session.get('user_agent')
    current_user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    if session_user_agent and session_user_agent != current_user_agent:
        logger.warning(
            f'Possible session hijacking detected for user: {request.user.username}'
        )
        return False
    
    # Store user agent in session
    if not session_user_agent:
        request.session['user_agent'] = current_user_agent
    
    return True


# ==========================================
# PASSWORD STRENGTH VALIDATION
# ==========================================

def validate_password_strength(password):
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not any(char.isdigit() for char in password):
        return False, 'Password must contain at least one number'
    
    if not any(char.isupper() for char in password):
        return False, 'Password must contain at least one uppercase letter'
    
    if not any(char.islower() for char in password):
        return False, 'Password must contain at least one lowercase letter'
    
    # Check for common passwords
    common_passwords = ['password', '12345678', 'qwerty', 'admin123']
    if password.lower() in common_passwords:
        return False, 'Password is too common. Please choose a stronger password'
    
    return True, ''


# ==========================================
# SQL INJECTION PREVENTION
# ==========================================

def is_sql_injection_attempt(text):
    """Detect potential SQL injection attempts"""
    if not text:
        return False
    
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'UNION', 'OR 1=1', 'OR 1 = 1', '--', '/*', '*/', 'EXEC', 'EXECUTE'
    ]
    
    text_upper = text.upper()
    for keyword in sql_keywords:
        if keyword in text_upper:
            logger.error(f'Potential SQL injection attempt detected: {text}')
            return True
    
    return False


# ==========================================
# FILE UPLOAD SECURITY
# ==========================================

def validate_file_upload(file):
    """Validate uploaded files"""
    # Check file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        return False, 'File size exceeds 5MB limit'
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
    file_ext = file.name.lower().split('.')[-1]
    if f'.{file_ext}' not in allowed_extensions:
        return False, f'File type .{file_ext} is not allowed'
    
    return True, ''


# ==========================================
# CSRF TOKEN VALIDATION
# ==========================================

def validate_csrf_token(request):
    """Additional CSRF token validation"""
    csrf_token = request.META.get('CSRF_COOKIE')
    if not csrf_token:
        logger.warning('Missing CSRF token in request')
        return False
    return True
