#!/usr/bin/env python
"""
Create migration for security models
Run this to generate migration for TwoFactorAuth, EmailVerification, etc.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

print("=" * 70)
print("  CREATING SECURITY MODELS MIGRATION")
print("=" * 70)
print()

# First, we need to add the security models to models.py
# Let's check if they're already there
from core_blood_system import models

# Import security models
from core_blood_system.advanced_security import (
    TwoFactorAuth,
    EmailVerification,
    UserActivityLog,
    UserSession,
    AdminAuditLog
)

print("✅ Security models imported successfully:")
print(f"   - TwoFactorAuth")
print(f"   - EmailVerification")
print(f"   - UserActivityLog")
print(f"   - UserSession")
print(f"   - AdminAuditLog")
print()

# Now create migrations
print("Creating migrations...")
try:
    call_command('makemigrations', 'core_blood_system')
    print()
    print("✅ Migration created successfully!")
    print()
    print("=" * 70)
    print("  NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Run locally:")
    print("   python manage.py migrate")
    print()
    print("2. Commit and push:")
    print("   git add .")
    print("   git commit -m 'Add security models migration'")
    print("   git push origin main")
    print()
    print("3. Deploy to PythonAnywhere:")
    print("   cd /home/kibeterick/blood_management_fullstack")
    print("   git pull origin main")
    print("   python manage.py migrate")
    print("   touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
    print()
    print("4. Reload web app at:")
    print("   https://www.pythonanywhere.com/user/kibeterick/webapps/")
    print()
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("The security models need to be in models.py for Django to detect them.")
    print("Let me add them now...")
