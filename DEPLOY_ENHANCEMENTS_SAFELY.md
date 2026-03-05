# Deploy Advanced Features to PythonAnywhere

## ⚠️ IMPORTANT WARNING
These features require database changes. Your site could break if not done carefully.
I recommend doing this during low-traffic hours.

## What We'll Deploy

### 1. Enhanced Inventory Management
- Track blood unit expiration dates
- Set inventory thresholds (minimum, critical, optimal levels)
- View expiring units dashboard

### 2. Email Notifications (Basic)
- Appointment confirmations
- Donation status updates
- Low stock alerts to admins

### 3. SMS Notifications (Optional - Requires paid service)
- Requires Twilio account (costs money)
- Can skip this for now

## Step-by-Step Deployment

### Step 1: Backup Your Database
```bash
cd /home/kibeterick/blood_management_fullstack
python manage.py dumpdata > backup_before_enhancements.json
```

### Step 2: Add New Database Fields
The BloodInventory model needs these new fields:
- `critical_threshold` (integer)
- `optimal_level` (integer)  
- `alert_sent_at` (datetime, nullable)

### Step 3: Create and Run Migration
```bash
cd /home/kibeterick/blood_management_fullstack
python manage.py makemigrations core_blood_system
python manage.py migrate
```

### Step 4: Uncomment Enhancement Code
Need to uncomment:
- `InventoryThresholdForm` in forms.py
- Inventory views and URLs
- Email notification code

### Step 5: Configure Email Settings
Add to settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### Step 6: Reload Site
```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

## What WON'T Work on PythonAnywhere Free Tier

❌ **Celery Background Tasks** - Requires paid account
- Automated daily stock checks
- Scheduled appointment reminders
- Background email sending

These need a worker process which isn't available on free tier.

## Alternative: Manual Triggers

Instead of automatic background tasks, you can:
1. Manually check low stock from admin dashboard
2. Send notifications when approving/rejecting donations
3. Run management commands manually when needed

## Recommendation

I suggest we deploy this in phases:
1. **Phase 1** (Safe): Just add database fields, keep features disabled
2. **Phase 2** (Test): Enable inventory dashboard only
3. **Phase 3** (Full): Enable email notifications

Would you like me to proceed with Phase 1 first?
