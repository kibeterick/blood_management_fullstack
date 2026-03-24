#!/usr/bin/env python
"""
Fix admin user role on PythonAnywhere
This script sets the admin user's role to 'admin' so they get full admin navigation
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

def fix_admin_role():
    """Set admin user role to 'admin'"""
    try:
        # Find the admin user
        admin_user = CustomUser.objects.get(username='admin')
        
        print(f"Found user: {admin_user.username}")
        print(f"Current role: {admin_user.role}")
        print(f"Is superuser: {admin_user.is_superuser}")
        print(f"Is staff: {admin_user.is_staff}")
        
        # Set role to admin
        admin_user.role = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        print("\n✅ SUCCESS!")
        print(f"Updated role to: {admin_user.role}")
        print(f"Is superuser: {admin_user.is_superuser}")
        print(f"Is staff: {admin_user.is_staff}")
        print("\nThe admin user now has full administrator access!")
        
    except CustomUser.DoesNotExist:
        print("❌ ERROR: Admin user not found!")
        print("Available users:")
        for user in CustomUser.objects.all():
            print(f"  - {user.username} (role: {user.role})")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    fix_admin_role()
