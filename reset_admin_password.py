#!/usr/bin/env python
"""
Reset admin password to a known value
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

# Get the admin user
admin = CustomUser.objects.get(username='Admin1085')

# Set new password
new_password = 'Admin@2026'
admin.set_password(new_password)
admin.save()

print("=" * 60)
print("PASSWORD RESET SUCCESSFUL!")
print("=" * 60)
print(f"\nUsername: Admin1085")
print(f"New Password: {new_password}")
print("\nYou can now login with these credentials.")
print("\nIMPORTANT: Change this password after logging in!")
print("=" * 60)
