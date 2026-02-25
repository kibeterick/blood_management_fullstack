# 🩸 PythonAnywhere Deployment Guide

## Quick Deployment Steps

### Step 1: Open PythonAnywhere Console
1. Go to https://www.pythonanywhere.com
2. Login to your account (kibeterick)
3. Click on "Tasks" → "Consoles"
4. Open a new Bash console

### Step 2: Navigate to Project Directory
```bash
cd ~/blood_management_fullstack
```

### Step 3: Pull Latest Changes
```bash
git pull origin main
```

### Step 4: Activate Virtual Environment
```bash
source ~/.virtualenvs/blood-management/bin/activate
```

### Step 5: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 6: Run Migrations
```bash
python manage.py migrate
```

### Step 7: Set Up Admin User
```bash
python manage.py shell
```

Then run this Python code in the shell:
```python
from core_blood_system.models import CustomUser

# Update or create admin user
try:
    admin = CustomUser.objects.get(username='admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
    print("Admin user updated")
except CustomUser.DoesNotExist:
    admin = CustomUser.objects.create_user(
        username='admin',
        email='admin@bloodsystem.com',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        role='admin',
        is_staff=True,
        is_superuser=True
    )
    print("Admin user created")

exit()
```

### Step 8: Reload Web App
1. Go to https://www.pythonanywhere.com/user/kibeterick/webapps/
2. Click the "Reload" button for your web app

**OR** run this command in console:
```bash
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
```

## ✅ Deployment Complete!

Your enhanced Blood Management System is now live at:
**https://kibeterick.pythonanywhere.com**

### New Features Available:
- ✅ Personalized welcome messages with time-based greetings
- ✅ Welcome modal popup on login
- ✅ User Management system (admin only)
- ✅ Enhanced registration page with welcome message
- ✅ Fixed admin login (username: admin, password: admin123)
- ✅ All previous features maintained

### Admin Access:
- **Username:** admin
- **Password:** admin123
- **URL:** https://kibeterick.pythonanywhere.com/login/

### Test the New Features:
1. Login as admin to see the welcome modal
2. Visit User Management at `/users/`
3. Try registering a new user to see the welcome message
4. Test the time-based greetings (Good morning/afternoon/evening)

---

**Note:** If you encounter any issues, check the error logs in your PythonAnywhere dashboard under "Tasks" → "Error logs".