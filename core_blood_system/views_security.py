"""
Views for Advanced Security Features
Handles 2FA, Activity Logs, Session Management, Email Verification
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from core_blood_system.models import (
    TwoFactorAuth,
    EmailVerification,
    UserActivityLog,
    UserSession,
    AdminAuditLog
)
from core_blood_system import advanced_security
from core_blood_system.security import get_client_ip, log_user_action
import json


# ==========================================
# SECURITY DASHBOARD
# ==========================================

@login_required
def security_dashboard(request):
    """Main security settings page"""
    user = request.user
    
    # Get 2FA status
    try:
        two_factor = TwoFactorAuth.objects.get(user=user)
        has_2fa = two_factor.is_enabled
    except TwoFactorAuth.DoesNotExist:
        has_2fa = False
    
    # Get recent activity (last 10)
    recent_activity = UserActivityLog.objects.filter(user=user)[:10]
    
    # Get active sessions
    active_sessions = UserSession.objects.filter(user=user, is_active=True)
    current_session_key = request.session.session_key
    
    # Email verification status
    email_verified = user.email_verified if hasattr(user, 'email_verified') else True
    
    context = {
        'has_2fa': has_2fa,
        'recent_activity': recent_activity,
        'active_sessions': active_sessions,
        'current_session_key': current_session_key,
        'email_verified': email_verified,
    }
    
    return render(request, 'security/dashboard.html', context)


# ==========================================
# TWO-FACTOR AUTHENTICATION (2FA)
# ==========================================

@login_required
def setup_2fa(request):
    """Setup 2FA for user"""
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            # Generate new 2FA secret
            two_factor = advanced_security.generate_2fa_secret(user)
            qr_code = advanced_security.generate_qr_code(two_factor)
            backup_codes = advanced_security.get_backup_codes_list(two_factor)
            
            request.session['2fa_setup_secret'] = two_factor.secret_key
            
            return render(request, 'security/setup_2fa.html', {
                'qr_code': qr_code,
                'secret_key': two_factor.secret_key,
                'backup_codes': backup_codes,
                'step': 'verify'
            })
        
        elif action == 'verify':
            # Verify 2FA code
            token = request.POST.get('token', '').strip()
            secret_key = request.session.get('2fa_setup_secret')
            
            if not secret_key:
                messages.error(request, 'Session expired. Please start again.')
                return redirect('setup_2fa')
            
            try:
                two_factor = TwoFactorAuth.objects.get(user=user, secret_key=secret_key)
                
                if advanced_security.verify_2fa_token(two_factor, token):
                    two_factor.is_enabled = True
                    two_factor.save()
                    
                    # Log activity
                    advanced_security.log_user_activity(user, '2fa_enabled', request)
                    
                    del request.session['2fa_setup_secret']
                    messages.success(request, '2FA enabled successfully!')
                    return redirect('security_dashboard')
                else:
                    messages.error(request, 'Invalid code. Please try again.')
            except TwoFactorAuth.DoesNotExist:
                messages.error(request, 'Setup session not found. Please start again.')
                return redirect('setup_2fa')
    
    # GET request - show initial setup page
    try:
        two_factor = TwoFactorAuth.objects.get(user=user)
        if two_factor.is_enabled:
            messages.info(request, '2FA is already enabled.')
            return redirect('security_dashboard')
    except TwoFactorAuth.DoesNotExist:
        pass
    
    return render(request, 'security/setup_2fa.html', {'step': 'start'})


@login_required
def disable_2fa(request):
    """Disable 2FA for user"""
    if request.method == 'POST':
        user = request.user
        password = request.POST.get('password')
        
        # Verify password
        if not user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return redirect('security_dashboard')
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            two_factor.is_enabled = False
            two_factor.save()
            
            # Log activity
            advanced_security.log_user_activity(user, '2fa_disabled', request)
            
            messages.success(request, '2FA disabled successfully.')
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, '2FA is not enabled.')
    
    return redirect('security_dashboard')


# ==========================================
# ACTIVITY LOGS
# ==========================================

@login_required
def activity_log(request):
    """View user's activity log"""
    user = request.user
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    days = int(request.GET.get('days', 30))
    
    # Build query
    activities = UserActivityLog.objects.filter(user=user)
    
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    if days:
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        activities = activities.filter(timestamp__gte=start_date)
    
    activities = activities[:100]  # Limit to 100 records
    
    # Get unique actions for filter dropdown
    action_choices = UserActivityLog.ACTION_CHOICES
    
    context = {
        'activities': activities,
        'action_choices': action_choices,
        'selected_action': action_filter,
        'selected_days': days,
    }
    
    return render(request, 'security/activity_log.html', context)


# ==========================================
# SESSION MANAGEMENT
# ==========================================

@login_required
def active_sessions(request):
    """View and manage active sessions"""
    user = request.user
    current_session_key = request.session.session_key
    
    # Update current session
    advanced_security.create_user_session(user, request)
    
    # Get all active sessions
    sessions = UserSession.objects.filter(user=user, is_active=True)
    
    context = {
        'sessions': sessions,
        'current_session_key': current_session_key,
    }
    
    return render(request, 'security/active_sessions.html', context)


@login_required
def terminate_session(request, session_key):
    """Terminate a specific session"""
    if request.method == 'POST':
        user = request.user
        current_session_key = request.session.session_key
        
        # Don't allow terminating current session
        if session_key == current_session_key:
            messages.error(request, 'Cannot terminate current session. Use logout instead.')
            return redirect('active_sessions')
        
        # Terminate session
        try:
            session = UserSession.objects.get(session_key=session_key, user=user)
            advanced_security.terminate_session(session_key)
            
            # Log activity
            advanced_security.log_user_activity(
                user, 'session_terminated', request,
                details=f'Terminated session from {session.device_info}'
            )
            
            messages.success(request, 'Session terminated successfully.')
        except UserSession.DoesNotExist:
            messages.error(request, 'Session not found.')
    
    return redirect('active_sessions')


@login_required
def terminate_all_sessions(request):
    """Terminate all sessions except current"""
    if request.method == 'POST':
        user = request.user
        current_session_key = request.session.session_key
        
        count = advanced_security.terminate_all_sessions_except_current(user, current_session_key)
        
        # Log activity
        advanced_security.log_user_activity(
            user, 'session_terminated', request,
            details=f'Terminated {count} other sessions'
        )
        
        messages.success(request, f'Terminated {count} other session(s).')
    
    return redirect('active_sessions')


# ==========================================
# EMAIL VERIFICATION
# ==========================================

def verify_email(request, token):
    """Verify user's email address"""
    try:
        verification = EmailVerification.objects.get(token=token)
        
        if not advanced_security.is_verification_valid(verification):
            messages.error(request, 'Verification link has expired.')
            return redirect('login')
        
        # Mark as verified
        user = verification.user
        user.email_verified = True
        user.save()
        
        verification.is_used = True
        verification.save()
        
        # Log activity
        if request.user.is_authenticated:
            advanced_security.log_user_activity(user, 'email_verified', request)
        
        messages.success(request, 'Email verified successfully! You can now login.')
        return redirect('login')
        
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('login')


@login_required
def resend_verification_email(request):
    """Resend email verification"""
    user = request.user
    
    if hasattr(user, 'email_verified') and user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('security_dashboard')
    
    # Create new verification token
    verification = advanced_security.create_verification_token(user)
    advanced_security.send_verification_email(verification, request)
    
    messages.success(request, 'Verification email sent! Please check your inbox.')
    return redirect('security_dashboard')


# ==========================================
# ADMIN AUDIT TRAIL
# ==========================================

@login_required
def admin_audit_trail(request):
    """View admin audit trail (admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('user_dashboard')
    
    # Get filter parameters
    admin_filter = request.GET.get('admin', '')
    action_filter = request.GET.get('action', '')
    model_filter = request.GET.get('model', '')
    days = int(request.GET.get('days', 30))
    
    # Build query
    logs = AdminAuditLog.objects.all()
    
    if admin_filter:
        logs = logs.filter(admin_user__username__icontains=admin_filter)
    
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    if model_filter:
        logs = logs.filter(model_name__icontains=model_filter)
    
    if days:
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        logs = logs.filter(timestamp__gte=start_date)
    
    logs = logs[:200]  # Limit to 200 records
    
    # Get unique values for filters
    action_types = AdminAuditLog.objects.values_list('action_type', flat=True).distinct()
    model_names = AdminAuditLog.objects.values_list('model_name', flat=True).distinct()
    
    context = {
        'logs': logs,
        'action_types': action_types,
        'model_names': model_names,
        'selected_admin': admin_filter,
        'selected_action': action_filter,
        'selected_model': model_filter,
        'selected_days': days,
    }
    
    return render(request, 'security/admin_audit_trail.html', context)


# ==========================================
# API ENDPOINTS
# ==========================================

@login_required
def check_2fa_status(request):
    """API endpoint to check 2FA status"""
    try:
        two_factor = TwoFactorAuth.objects.get(user=request.user)
        return JsonResponse({
            'enabled': two_factor.is_enabled,
            'last_used': two_factor.last_used.isoformat() if two_factor.last_used else None
        })
    except TwoFactorAuth.DoesNotExist:
        return JsonResponse({'enabled': False})


@login_required
def get_activity_stats(request):
    """API endpoint to get activity statistics"""
    user = request.user
    
    from datetime import timedelta
    now = timezone.now()
    
    # Count activities by type in last 30 days
    thirty_days_ago = now - timedelta(days=30)
    
    stats = {}
    for action, label in UserActivityLog.ACTION_CHOICES:
        count = UserActivityLog.objects.filter(
            user=user,
            action=action,
            timestamp__gte=thirty_days_ago
        ).count()
        stats[action] = count
    
    return JsonResponse(stats)
