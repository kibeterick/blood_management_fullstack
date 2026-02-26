# 🔧 Troubleshooting Guide - Features 2-5

## Common Issues and Solutions

---

## Issue 1: Notification Bell Not Showing

### Symptoms:
- No bell icon in navigation
- Badge not visible

### Solutions:

**A. Check Browser Console**
```
1. Press F12 to open developer tools
2. Go to Console tab
3. Look for JavaScript errors
4. Check if fetch to /api/notifications/unread-count/ succeeds
```

**B. Clear Browser Cache**
```
1. Press Ctrl+Shift+Delete
2. Clear cached images and files
3. Reload page (Ctrl+F5)
```

**C. Verify Template Updated**
```bash
# On PythonAnywhere
cd ~/blood_management_fullstack
git pull origin main
python manage.py collectstatic --noinput
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

---

## Issue 2: Charts Not Displaying (Analytics)

### Symptoms:
- Analytics page loads but charts are blank
- Console shows Chart.js errors

### Solutions:

**A. Check Chart.js CDN**
```
1. Open browser console (F12)
2. Go to Network tab
3. Reload page
4. Check if Chart.js loads (should be ~200KB)
5. If 404, CDN might be blocked
```

**B. Verify Data Format**
```python
# Check analytics data in Django shell
python manage.py shell

from core_blood_system.enhancements import get_dashboard_analytics
analytics = get_dashboard_analytics()
print(analytics['monthly_trends'])
# Should return list of dicts with 'month', 'donations', 'units'
```

**C. Check Template Syntax**
```
1. Visit /analytics/
2. View page source (Ctrl+U)
3. Search for "monthlyData"
4. Verify JSON is properly formatted
```

---

## Issue 3: Matching System Not Finding Donors

### Symptoms:
- "Run Matching Algorithm" returns 0 matches
- No donors appear in results

### Solutions:

**A. Check Donor Eligibility**
```python
# Django shell
from core_blood_system.models import Donor
from datetime import datetime, timedelta

# Check available donors
available = Donor.objects.filter(is_available=True)
print(f"Available donors: {available.count()}")

# Check last donation dates
min_date = datetime.now().date() - timedelta(days=56)
eligible = available.filter(last_donation_date__lte=min_date)
print(f"Eligible donors: {eligible.count()}")
```

**B. Verify Blood Type Match**
```python
# Check if blood types match
from core_blood_system.models import BloodRequest
request = BloodRequest.objects.first()
print(f"Request blood type: {request.blood_type}")

donors = Donor.objects.filter(blood_type=request.blood_type)
print(f"Matching donors: {donors.count()}")
```

**C. Run Matching Manually**
```python
# Django shell
from core_blood_system.enhancements import match_donors_to_request
from core_blood_system.models import BloodRequest

request = BloodRequest.objects.get(id=1)  # Replace with actual ID
matches = match_donors_to_request(request)
print(f"Found {len(matches)} matches")
```

---

## Issue 4: QR Code Generation Fails

### Symptoms:
- Error when generating QR codes
- "No module named 'qrcode'" error

### Solutions:

**A. Install QR Code Package**
```bash
# On PythonAnywhere
cd ~/blood_management_fullstack
source venv/bin/activate
pip install qrcode[pil] Pillow
```

**B. Verify Installation**
```python
# Django shell
import qrcode
print("QR code package installed successfully")
```

**C. Check Media Settings**
```python
# In backend/settings.py, verify:
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Issue 5: 404 Errors on New URLs

### Symptoms:
- /notifications/ returns 404
- /analytics/ returns 404
- /matching/admin/ returns 404

### Solutions:

**A. Verify URLs File Updated**
```bash
# Check if urls.py has new imports
cd ~/blood_management_fullstack
grep "views_notifications" core_blood_system/urls.py
grep "views_matching" core_blood_system/urls.py
grep "views_analytics" core_blood_system/urls.py
grep "views_qrcode" core_blood_system/urls.py
```

**B. Check View Files Exist**
```bash
ls -la core_blood_system/views_*.py
# Should show:
# views_appointments.py
# views_notifications.py
# views_matching.py
# views_analytics.py
# views_qrcode.py
```

**C. Reload Application**
```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

---

## Issue 6: Import Errors

### Symptoms:
- "No module named 'core_blood_system.views_notifications'"
- Server error 500

### Solutions:

**A. Check File Permissions**
```bash
cd ~/blood_management_fullstack
chmod 644 core_blood_system/views_*.py
```

**B. Verify Python Syntax**
```bash
python -m py_compile core_blood_system/views_notifications.py
python -m py_compile core_blood_system/views_matching.py
python -m py_compile core_blood_system/views_analytics.py
python -m py_compile core_blood_system/views_qrcode.py
```

**C. Check __pycache__**
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete
```

---

## Issue 7: Static Files Not Loading

### Symptoms:
- CSS not applied
- JavaScript not working
- Images missing

### Solutions:

**A. Collect Static Files**
```bash
cd ~/blood_management_fullstack
source venv/bin/activate
python manage.py collectstatic --noinput
```

**B. Check Static Files Configuration**
```python
# In backend/settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

**C. Verify PythonAnywhere Static Files Mapping**
```
1. Go to PythonAnywhere Web tab
2. Check Static files section
3. Should have: /static/ → /home/kibeterick/blood_management_fullstack/staticfiles
```

---

## Issue 8: Database Errors

### Symptoms:
- "no such table: core_blood_system_notification"
- "no such column" errors

### Solutions:

**A. Run Migrations**
```bash
cd ~/blood_management_fullstack
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

**B. Check Migration Files**
```bash
ls -la core_blood_system/migrations/
# Should include 0004_donationappointment_matcheddonor_notification_qrcode_and_more.py
```

**C. Force Migration**
```bash
python manage.py migrate core_blood_system --fake-initial
python manage.py migrate
```

---

## Issue 9: Permission Denied Errors

### Symptoms:
- "Only administrators can access this page"
- Features not accessible

### Solutions:

**A. Check User Role**
```python
# Django shell
from core_blood_system.models import CustomUser
user = CustomUser.objects.get(username='admin')
print(f"Role: {user.role}")
print(f"Is staff: {user.is_staff}")
print(f"Is superuser: {user.is_superuser}")
```

**B. Update User Role**
```python
# If role is not 'admin'
user.role = 'admin'
user.is_staff = True
user.is_superuser = True
user.save()
```

---

## Issue 10: Mobile Display Issues

### Symptoms:
- Layout broken on mobile
- Navigation not responsive
- Charts overflow

### Solutions:

**A. Check Viewport Meta Tag**
```html
<!-- Should be in base.html -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**B. Test Responsive CSS**
```
1. Open browser developer tools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select mobile device
4. Test navigation and pages
```

**C. Clear Mobile Browser Cache**
```
1. On Android: Settings → Apps → Browser → Clear Cache
2. Or use incognito/private mode
```

---

## Quick Diagnostic Commands

### Check System Status
```bash
cd ~/blood_management_fullstack
source venv/bin/activate

# Check Python version
python --version

# Check Django version
python -c "import django; print(django.get_version())"

# Check installed packages
pip list | grep -E "qrcode|Pillow|reportlab|openpyxl"

# Test database connection
python manage.py check

# List migrations
python manage.py showmigrations core_blood_system
```

### View Logs
```bash
# Error log
tail -50 /var/log/kibeterick.pythonanywhere.com.error.log

# Server log
tail -50 /var/log/kibeterick.pythonanywhere.com.server.log

# Access log
tail -50 /var/log/kibeterick.pythonanywhere.com.access.log
```

### Test URLs
```bash
# Test if URLs are accessible
curl -I https://kibeterick.pythonanywhere.com/notifications/
curl -I https://kibeterick.pythonanywhere.com/analytics/
curl -I https://kibeterick.pythonanywhere.com/matching/admin/
```

---

## Emergency Reset

If everything is broken:

```bash
cd ~/blood_management_fullstack
source venv/bin/activate

# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt
pip install qrcode[pil] Pillow

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Clear cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete

# 6. Reload app
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py

# 7. Wait 30 seconds and test
```

---

## Getting Help

### Check These Files:
1. `VERIFY_DEPLOYMENT.md` - Testing checklist
2. `ALL_FEATURES_COMPLETE.md` - Feature documentation
3. `FEATURES_2_5_DEPLOYMENT.md` - Deployment guide

### Debug Mode:
```python
# Temporarily enable debug (NEVER in production long-term)
# In backend/settings.py
DEBUG = True

# Test, then immediately set back to:
DEBUG = False
```

### Contact Information:
- Check PythonAnywhere forums
- Review Django documentation
- Check browser console for specific errors

---

## Prevention Tips

1. **Always test locally first** before deploying
2. **Commit frequently** with clear messages
3. **Keep backups** of working code
4. **Monitor logs** regularly
5. **Test on mobile** after each deployment
6. **Clear cache** when updating templates
7. **Run migrations** after model changes
8. **Collect static** after CSS/JS changes

---

## Success Indicators

✅ No errors in browser console
✅ All URLs return 200 status
✅ Charts display with data
✅ Notification badge updates
✅ Mobile layout responsive
✅ No 404 or 500 errors
✅ Database queries work
✅ Static files load

If all above are ✅, your system is healthy!

---

**Remember: Most issues are solved by:**
1. Clearing cache
2. Collecting static files
3. Reloading the app
4. Checking browser console

Good luck! 🚀
