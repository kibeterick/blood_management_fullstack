# 🔐 Security Features Setup Guide

## ✅ What's Been Created

1. **Database Models** ✅
   - TwoFactorAuth
   - EmailVerification
   - UserActivityLog
   - UserSession
   - AdminAuditLog

2. **Views** ✅
   - Security Dashboard
   - 2FA Setup/Disable
   - Activity Log Viewer
   - Session Management
   - Email Verification
   - Admin Audit Trail

3. **Migration** ✅
   - Database tables created

---

## 📋 Next Steps to Complete Setup

### Step 1: Add URLs

Add these to `core_blood_system/urls.py`:

```python
from core_blood_system import views_security

# Security Features URLs
path('security/', views_security.security_dashboard, name='security_dashboard'),
path('security/setup-2fa/', views_security.setup_2fa, name='setup_2fa'),
path('security/disable-2fa/', views_security.disable_2fa, name='disable_2fa'),
path('security/activity-log/', views_security.activity_log, name='activity_log'),
path('security/active-sessions/', views_security.active_sessions, name='active_sessions'),
path('security/terminate-session/<str:session_key>/', views_security.terminate_session, name='terminate_session'),
path('security/terminate-all-sessions/', views_security.terminate_all_sessions, name='terminate_all_sessions'),
path('verify-email/<str:token>/', views_security.verify_email, name='verify_email'),
path('security/resend-verification/', views_security.resend_verification_email, name='resend_verification'),
path('admin/audit-trail/', views_security.admin_audit_trail, name='admin_audit_trail'),

# API Endpoints
path('api/security/2fa-status/', views_security.check_2fa_status, name='check_2fa_status'),
path('api/security/activity-stats/', views_security.get_activity_stats, name='get_activity_stats'),
```

### Step 2: Update User Model

Add to your User model in `core_blood_system/models.py`:

```python
class User(AbstractUser):
    # ... existing fields ...
    email_verified = models.BooleanField(default=False)
    
    # Add this method
    def has_2fa_enabled(self):
        try:
            return self.two_factor.is_enabled
        except:
            return False
```

### Step 3: Update Login View

Modify your login view to check for 2FA:

```python
from core_blood_system.advanced_security import TwoFactorAuth, UserSession, UserActivityLog

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if 2FA is enabled
            try:
                two_factor = TwoFactorAuth.objects.get(user=user, is_enabled=True)
                # Store user ID in session for 2FA verification
                request.session['2fa_user_id'] = user.id
                return redirect('verify_2fa')
            except TwoFactorAuth.DoesNotExist:
                # No 2FA, login normally
                login(request, user)
                
                # Create session record
                UserSession.create_session(user, request)
                
                # Log activity
                UserActivityLog.log_activity(user, 'login', request)
                
                return redirect('dashboard')
        else:
            # Log failed login
            UserActivityLog.objects.create(
                user=user if user else None,
                action='failed_login',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=False
            )
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'login.html')
```

### Step 4: Create 2FA Verification View

Add this new view:

```python
def verify_2fa(request):
    """Verify 2FA code during login"""
    user_id = request.session.get('2fa_user_id')
    
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            
            if two_factor.verify_token(token):
                # 2FA successful, login user
                login(request, user)
                
                # Create session record
                UserSession.create_session(user, request)
                
                # Log activity
                UserActivityLog.log_activity(user, 'login', request)
                
                # Clear 2FA session
                del request.session['2fa_user_id']
                
                messages.success(request, 'Login successful!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid 2FA code')
        except TwoFactorAuth.DoesNotExist:
            messages.error(request, '2FA not configured')
            return redirect('login')
    
    return render(request, 'security/verify_2fa.html', {'user': user})
```

### Step 5: Update Logout View

Modify logout to update session:

```python
def logout_view(request):
    if request.user.is_authenticated:
        # Log activity
        UserActivityLog.log_activity(request.user, 'logout', request)
        
        # Mark session as inactive
        session_key = request.session.session_key
        UserSession.objects.filter(session_key=session_key).update(is_active=False)
    
    logout(request)
    return redirect('login')
```

### Step 6: Add Navigation Links

Add to your `base.html` navigation:

```html
{% if user.is_authenticated %}
    <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" id="securityDropdown" role="button" data-bs-toggle="dropdown">
            <i class="bi bi-shield-lock"></i> Security
        </a>
        <ul class="dropdown-menu" aria-labelledby="securityDropdown">
            <li><a class="dropdown-item" href="{% url 'security_dashboard' %}">
                <i class="bi bi-shield-check"></i> Security Settings
            </a></li>
            <li><a class="dropdown-item" href="{% url 'activity_log' %}">
                <i class="bi bi-clock-history"></i> Activity Log
            </a></li>
            <li><a class="dropdown-item" href="{% url 'active_sessions' %}">
                <i class="bi bi-phone"></i> Active Sessions
            </a></li>
            {% if user.role == 'admin' %}
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item" href="{% url 'admin_audit_trail' %}">
                <i class="bi bi-journal-text"></i> Audit Trail
            </a></li>
            {% endif %}
        </ul>
    </li>
{% endif %}
```

### Step 7: Install Required Packages

```bash
pip install pyotp qrcode[pil] pillow
```

### Step 8: Configure Email (Optional)

Add to `backend/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'Blood Management System <noreply@bloodsystem.com>'

# For development, use console backend:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## 🎨 Create Templates

Create these template files in `core_blood_system/templates/security/`:

1. **dashboard.html** - Main security settings page
2. **setup_2fa.html** - 2FA setup wizard
3. **verify_2fa.html** - 2FA code entry during login
4. **activity_log.html** - User activity history
5. **active_sessions.html** - Session management
6. **admin_audit_trail.html** - Admin audit log

---

## 🧪 Testing

### Test 2FA:
1. Login as a user
2. Go to Security Settings
3. Click "Enable 2FA"
4. Scan QR code with Google Authenticator
5. Enter 6-digit code
6. Save backup codes
7. Logout and login again
8. Enter 2FA code

### Test Activity Log:
1. Login from different devices/browsers
2. Go to Activity Log
3. See all your logins with IP and device info

### Test Session Management:
1. Login from multiple devices
2. Go to Active Sessions
3. See all logged-in devices
4. Logout from specific device
5. Or logout from all other devices

### Test Admin Audit Trail:
1. Login as admin
2. Make some changes (edit user, approve donation, etc.)
3. Go to Admin → Audit Trail
4. See all admin actions logged

---

## 📊 What Users Will See

### Security Dashboard:
```
🔐 Security Settings

Two-Factor Authentication: ❌ Disabled
[Enable 2FA]

Email Verification: ✅ Verified

Recent Activity:
- Login from Windows - Chrome (2 hours ago)
- Login from Android - Chrome (Yesterday)

Active Sessions: 2 devices
[Manage Sessions]
```

### After Enabling 2FA:
```
🔐 Two-Factor Authentication

Status: ✅ Enabled
Last Used: 2 hours ago

[View Backup Codes]
[Disable 2FA]
```

### Activity Log:
```
📊 Activity Log

Filter: [All Actions ▼] [Last 30 Days ▼] [Apply]

Date/Time          | Action          | Device           | IP Address      | Status
-------------------|-----------------|------------------|-----------------|--------
Feb 28, 10:30 AM   | Login           | Windows - Chrome | 197.xxx.xxx.xxx | ✅
Feb 27, 3:45 PM    | Login           | Android - Chrome | 105.xxx.xxx.xxx | ✅
Feb 27, 2:15 PM    | Password Change | Windows - Chrome | 197.xxx.xxx.xxx | ✅
Feb 26, 9:00 AM    | Failed Login    | Unknown          | 41.xxx.xxx.xxx  | ❌
```

### Active Sessions:
```
📱 Active Sessions

Current Session:
Windows - Chrome
IP: 197.xxx.xxx.xxx
Last Active: Just now
[This Device]

Other Sessions:
Android - Chrome
IP: 105.xxx.xxx.xxx
Last Active: 2 hours ago
[Logout This Device]

[Logout All Other Devices]
```

---

## 🚀 Deployment to PythonAnywhere

1. **Commit and push:**
```bash
git add .
git commit -m "Add advanced security features: 2FA, activity logs, session management"
git push origin main
```

2. **On PythonAnywhere:**
```bash
cd /home/kibeterick/blood_management_fullstack
git pull origin main
pip install pyotp qrcode[pil] pillow
python manage.py migrate
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

3. **Reload web app**

---

## ✅ Summary

You now have:
- ✅ Two-Factor Authentication (2FA)
- ✅ Email Verification
- ✅ User Activity Logs
- ✅ Session Management
- ✅ Admin Audit Trail
- ✅ All database tables created
- ✅ All views created
- ✅ Ready to add URLs and templates

**Next:** Add the URLs to `urls.py` and create the template files!

---
