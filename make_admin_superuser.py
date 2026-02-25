#!/usr/bin/env python
"""
Make admin user a superuser so they can access Django admin
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

# Get admin user
admin = CustomUser.objects.get(username='admin')

# Make superuser
admin.is_superuser = True
admin.is_staff = True
admin.save()

print("=" * 60)
print("ADMIN USER UPDATED TO SUPERUSER!")
print("=" * 60)
print(f"\nUsername: {admin.username}")
print(f"Email: {admin.email}")
print(f"Role: {admin.role}")
print(f"Is Staff: {admin.is_staff}")
print(f"Is Superuser: {admin.is_superuser}")
print("\nYou can now access Django admin at /admin/")
print("=" * 60)
