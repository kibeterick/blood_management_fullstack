#!/usr/bin/env python
"""
Debug admin password issue
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from core_blood_system.models import CustomUser

# Get admin user
admin = CustomUser.objects.get(username='admin')

print("=" * 60)
print("ADMIN USER DEBUG")
print("=" * 60)
print(f"Username: {admin.username}")
print(f"Email: {admin.email}")
print(f"Role: {admin.role}")
print(f"Is Active: {admin.is_active}")
print(f"Password Hash: {admin.password[:50]}...")
print(f"Has Usable Password: {admin.has_usable_password()}")

# Test various passwords
print("\n" + "=" * 60)
print("TESTING PASSWORDS")
print("=" * 60)

passwords_to_test = [
    'Admin@2026',
    'admin',
    'admin123',
    'Admin1085',
]

for pwd in passwords_to_test:
    user = authenticate(username='admin', password=pwd)
    if user:
        print(f"✓ SUCCESS with password: '{pwd}'")
        break
    else:
        print(f"✗ Failed with password: '{pwd}'")
        # Check if password matches
        if admin.check_password(pwd):
            print(f"  BUT check_password() returned True! Auth backend issue.")

# If none worked, reset password
if not any(authenticate(username='admin', password=p) for p in passwords_to_test):
    print("\n" + "=" * 60)
    print("RESETTING PASSWORD")
    print("=" * 60)
    new_password = 'admin123'
    admin.set_password(new_password)
    admin.save()
    
    # Verify it works
    user = authenticate(username='admin', password=new_password)
    if user:
        print(f"✓ Password reset successful!")
        print(f"\nNew credentials:")
        print(f"  Username: admin")
        print(f"  Password: {new_password}")
    else:
        print(f"✗ Password reset failed!")

print("=" * 60)
