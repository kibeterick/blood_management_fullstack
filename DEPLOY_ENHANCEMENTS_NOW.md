# Deploy Blood Management Enhancements - Quick Start Guide

## 🚀 What's Ready to Deploy

Tasks 1-6 are complete and ready for production:
- ✅ Blood Inventory Management System
- ✅ Email Notification Service
- ✅ Real-time Dashboard with Charts
- ✅ Expiration Tracking
- ✅ Low Stock Alerts

## 📋 Pre-Deployment Checklist

- [ ] Database backup completed
- [ ] Git repository up to date
- [ ] PythonAnywhere console access ready
- [ ] Admin credentials available (username: admin, password: E38736434k)

## 🔧 Deployment Steps for PythonAnywhere

### Step 1: Update Code on PythonAnywhere

```bash
cd /home/kibeterick/blood_management_fullstack
git add .
git commit -m "Add blood inventory management and email notifications"
git push origin main
```

Then on PythonAnywhere console:

```bash
cd /home/kibeterick/blood_management_fullstack
git pull origin main
```

### Step 2: Run Database Migrations

```bash
cd /home/kibeterick/blood_management_fullstack
python manage.py makemigrations core_blood_system
python manage.py migrate
```

### Step 3: Create Initial Inventory Records

```bash
python manage.py shell
```

Then in the Python shell:

```python
from core_blood_system.models import BloodInventory, BLOOD_TYPE_CHOICES

# Create inventory records for all blood types
for blood_type, display_name in BLOOD_TYPE_CHOICES:
    inventory, created = BloodInventory.objects.get_or_create(
        blood_type=blood_type,
        defaults={
            'units_available': 0,
            'minimum_threshold': 5,
            'critical_threshold': 2,
            'optimal_level': 20
        }
    )
    if created:
        print(f"Created inventory for {blood_type}")
    else:
        # Add new fields to existing records
        if not hasattr(inventory, 'critical_threshold') or inventory.critical_threshold is None:
            inventory.critical_threshold = 2
        if not hasattr(inventory, 'optimal_level') or inventory.optimal_level is None:
            inventory.optimal_level = 20
        inventory.save()
        print(f"Updated inventory for {blood_type}")

exit()
```

### Step 4: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 5: Reload Web App

```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

Or use the PythonAnywhere web interface:
1. Go to Web tab
2. Click "Reload kibeterick.pythonanywhere.com"

### Step 6: Verify Deployment

Visit these URLs to test:
1. https://kibeterick.pythonanywhere.com/inventory/ (Inventory Dashboard)
2. https://kibeterick.pythonanywhere.com/inventory/add-unit/ (Add Blood Unit)
3. https://kibeterick.pythonanywhere.com/inventory/expiration/ (Expiration List)
4. https://kibeterick.pythonanywhere.com/inventory/configure-thresholds/ (Configure Thresholds)

## 🎯 Quick Test Procedure

### Test 1: View Inventory Dashboard
1. Login as admin
2. Navigate to `/inventory/`
3. Verify you see all 8 blood types
4. Check that the chart displays correctly
5. Verify statistics cards show correct data

### Test 2: Add a Blood Unit
1. Click "Add Blood Unit" button
2. Fill in the form:
   - Blood Type: O+
   - Unit Number: TEST-001
   - Donation Date: Today's date
   - Expiration Date: (auto-calculated to 42 days from today)
   - Volume: 450ml
3. Submit the form
4. Verify the unit appears in the dashboard
5. Check that O+ inventory count increased

### Test 3: Configure Thresholds
1. Navigate to `/inventory/configure-thresholds/`
2. Update thresholds for A+ blood type:
   - Critical: 2
   - Minimum: 5
   - Optimal: 20
3. Save changes
4. Verify the changes are reflected in the dashboard

### Test 4: Expiration Tracking
1. Navigate to `/inventory/expiration/`
2. Verify units are categorized correctly:
   - Expired (red)
   - Expiring Soon (yellow)
   - Good Condition (green)
3. Test "Mark as Used" button
4. Verify inventory count updates

### Test 5: Email Notifications (if configured)
1. Approve a donation
2. Check that inventory updates automatically
3. If stock falls below threshold, verify admin receives email alert

## ⚙️ Configuration (Optional)

### Email Configuration

Add to `backend/settings.py` or `backend/production_settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Blood Bank <noreply@bloodbank.com>'
BLOOD_BANK_CONTACT = '+254-XXX-XXXXXX'  # Your contact number
```

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use that password in EMAIL_HOST_PASSWORD

## 🐛 Troubleshooting

### Issue: "No module named 'core_blood_system.inventory_manager'"

**Solution:**
```bash
cd /home/kibeterick/blood_management_fullstack
python manage.py collectstatic --noinput
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

### Issue: "BloodUnit matching query does not exist"

**Solution:** The BloodUnit model needs to be migrated. Run:
```bash
python manage.py makemigrations core_blood_system
python manage.py migrate
```

### Issue: Chart not displaying

**Solution:** Clear browser cache (Ctrl + Shift + R) or try incognito mode

### Issue: "Permission denied" on inventory pages

**Solution:** Ensure you're logged in as an admin user. Check user role:
```python
python manage.py shell
from core_blood_system.models import CustomUser
user = CustomUser.objects.get(username='admin')
print(user.role)  # Should be 'admin'
```

### Issue: Email notifications not sending

**Solution:** 
1. Check email configuration in settings
2. Verify SMTP credentials are correct
3. Check NotificationLog model for error messages:
```python
python manage.py shell
from core_blood_system.models import NotificationLog
logs = NotificationLog.objects.filter(status='failed').order_by('-created_at')[:5]
for log in logs:
    print(f"{log.notification_type}: {log.error_message}")
```

## 📊 Post-Deployment Monitoring

### Check Inventory Status
```python
python manage.py shell
from core_blood_system.models import BloodInventory
for inv in BloodInventory.objects.all():
    print(f"{inv.blood_type}: {inv.units_available} units ({inv.get_status()})")
```

### Check Notification Logs
```python
from core_blood_system.models import NotificationLog
recent = NotificationLog.objects.order_by('-created_at')[:10]
for log in recent:
    print(f"{log.created_at}: {log.notification_type} to {log.recipient} - {log.status}")
```

### Check Blood Units
```python
from core_blood_system.models import BloodUnit
from datetime import date, timedelta
expiring = BloodUnit.objects.filter(
    status='available',
    expiration_date__lte=date.today() + timedelta(days=7)
).count()
print(f"Units expiring within 7 days: {expiring}")
```

## 🎓 User Training

### For Admins:

**Daily Tasks:**
1. Check inventory dashboard for low stock alerts
2. Review expiring units list
3. Process donation approvals (auto-updates inventory)
4. Monitor notification logs

**Weekly Tasks:**
1. Review and adjust stock thresholds
2. Check for expired units
3. Generate inventory reports

**Monthly Tasks:**
1. Analyze inventory trends
2. Review notification effectiveness
3. Update optimal stock levels

### For Staff:

**When Receiving Donations:**
1. Record donation in system
2. Admin approves donation
3. System automatically creates blood unit
4. Inventory updates in real-time

**When Issuing Blood:**
1. Navigate to expiration list
2. Select unit (prioritize expiring soon)
3. Click "Mark as Used"
4. Inventory updates automatically

## 📱 Mobile Access

All features are mobile-responsive. Users can:
- View inventory dashboard on mobile
- Check expiration dates
- Receive email notifications
- Access from any device

## 🔐 Security Notes

- ✅ All inventory pages require admin authentication
- ✅ CSRF protection enabled on all forms
- ✅ SQL injection prevention via Django ORM
- ✅ XSS protection via template escaping
- ✅ Audit trail via NotificationLog

## 📈 Performance Tips

1. **Database Indexes:** Already added for optimal query performance
2. **Chart Rendering:** Client-side with Chart.js (no server load)
3. **API Calls:** Throttled to every 30 seconds
4. **Static Files:** Served via PythonAnywhere CDN

## 🎯 Success Criteria

Deployment is successful when:
- ✅ Inventory dashboard loads without errors
- ✅ All 8 blood types display correctly
- ✅ Chart visualization works
- ✅ Can add blood units successfully
- ✅ Expiration tracking functions properly
- ✅ Threshold configuration saves correctly
- ✅ Email notifications send (if configured)
- ✅ Mobile access works smoothly

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review error logs in PythonAnywhere
3. Check browser console for JavaScript errors
4. Verify database migrations completed successfully

## 🎉 What's Next

After successful deployment, you can:
1. Train staff on new features
2. Monitor system usage
3. Gather user feedback
4. Plan for remaining features (SMS, eligibility checker)

---

**Deployment Date:** March 5, 2026
**Version:** 1.0 - Inventory Management & Email Notifications
**Status:** Ready for Production
