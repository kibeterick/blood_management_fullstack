#!/usr/bin/env python
"""
Set a simple password for admin
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

# Set simple password
new_password = 'admin123'
admin.set_password(new_password)
admin.save()

print("=" * 60)
print("PASSWORD UPDATED!")
print("=" * 60)
print(f"\nUsername: admin")
print(f"Password: {new_password}")

# Verify it works
user = authenticate(username='admin', password=new_password)
if user:
    print(f"\n✓ Login test successful!")
    print(f"  User: {user.username}")
    print(f"  Role: {user.role}")
    print("\nYou can now login with these credentials.")
else:
    print(f"\n✗ Login test failed!")

print("=" * 60)
