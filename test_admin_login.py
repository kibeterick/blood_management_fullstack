#!/usr/bin/env python
"""
Test authentication for Admin1085
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from core_blood_system.models import CustomUser

# Get the admin user
admin = CustomUser.objects.get(username='Admin1085')
print("=" * 60)
print("ADMIN USER: Admin1085")
print("=" * 60)
print(f"Username: {admin.username}")
print(f"Email: {admin.email}")
print(f"Role: {admin.role}")
print(f"Is Active: {admin.is_active}")
print(f"Is Staff: {admin.is_staff}")
print(f"Has Usable Password: {admin.has_usable_password()}")

print("\n" + "=" * 60)
print("INSTRUCTIONS")
print("=" * 60)
print("\nTo login as admin, use:")
print(f"  Username: Admin1085")
print(f"  Password: [your password]")
print("\nIf you forgot your password, reset it with:")
print("  python manage.py changepassword Admin1085")
