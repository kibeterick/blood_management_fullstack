#!/usr/bin/env python
"""
Verify admin can login with Admin@2026
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate

# Test authentication
user = authenticate(username='admin', password='Admin@2026')

print("=" * 60)
print("LOGIN TEST")
print("=" * 60)
print(f"\nUsername: admin")
print(f"Password: Admin@2026")

if user:
    print(f"\n✓ SUCCESS! Authentication works!")
    print(f"  - User: {user.username}")
    print(f"  - Name: {user.first_name} {user.last_name}")
    print(f"  - Role: {user.role}")
    print(f"  - Email: {user.email}")
    print("\nYou can now login to the system!")
else:
    print(f"\n✗ FAILED! Authentication did not work.")
    print("The password may not have been set correctly.")

print("=" * 60)
