#!/usr/bin/env python
"""
Script to check admin user and test authentication
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from core_blood_system.models import CustomUser

def check_admin_user():
    print("=" * 60)
    print("ADMIN USER DIAGNOSTIC CHECK")
    print("=" * 60)
    
    # Check if admin user exists
    try:
        admin_user = CustomUser.objects.get(username='admin')
        print(f"\n✓ Admin user found!")
        print(f"  - Username: {admin_user.username}")
        print(f"  - Email: {admin_user.email}")
        print(f"  - First Name: {admin_user.first_name}")
        print(f"  - Last Name: {admin_user.last_name}")
        print(f"  - Role: {admin_user.role}")
        print(f"  - Is Active: {admin_user.is_active}")
        print(f"  - Is Staff: {admin_user.is_staff}")
        print(f"  - Is Superuser: {admin_user.is_superuser}")
        print(f"  - Has Usable Password: {admin_user.has_usable_password()}")
        
        # Test authentication with common passwords
        print("\n" + "=" * 60)
        print("TESTING AUTHENTICATION")
        print("=" * 60)
        
        test_passwords = ['admin', 'admin123', 'password', 'Admin@123']
        
        for pwd in test_passwords:
            user = authenticate(username='admin', password=pwd)
            if user:
                print(f"\n✓ SUCCESS! Password is: '{pwd}'")
                print(f"  - User authenticated: {user.username}")
                print(f"  - User role: {user.role}")
                return
            else:
                print(f"✗ Failed with password: '{pwd}'")
        
        print("\n" + "=" * 60)
        print("SOLUTION")
        print("=" * 60)
        print("\nNone of the common passwords worked.")
        print("You need to reset the admin password.")
        print("\nRun this command:")
        print("  python manage.py changepassword admin")
        print("\nOr create a new admin user:")
        print("  python manage.py createsuperuser")
        
    except CustomUser.DoesNotExist:
        print("\n✗ Admin user does not exist!")
        print("\n" + "=" * 60)
        print("SOLUTION")
        print("=" * 60)
        print("\nYou need to create an admin user.")
        print("\nOption 1 - Create superuser:")
        print("  python manage.py createsuperuser")
        print("\nOption 2 - Use the custom command:")
        print("  python manage.py create_admin")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # List all users
    print("\n" + "=" * 60)
    print("ALL USERS IN DATABASE")
    print("=" * 60)
    users = CustomUser.objects.all()
    if users.exists():
        for user in users:
            print(f"\n- Username: {user.username}")
            print(f"  Role: {user.role}")
            print(f"  Email: {user.email}")
            print(f"  Active: {user.is_active}")
    else:
        print("\nNo users found in database!")

if __name__ == '__main__':
    check_admin_user()
