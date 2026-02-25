#!/usr/bin/env python
"""
Change Admin1085 username to admin
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

try:
    # Get the admin user
    admin = CustomUser.objects.get(username='Admin1085')
    
    # Change username to 'admin'
    admin.username = 'admin'
    admin.save()
    
    print("=" * 60)
    print("USERNAME CHANGED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nOld Username: Admin1085")
    print(f"New Username: admin")
    print(f"Password: Admin@2026")
    print(f"Email: {admin.email}")
    print(f"Role: {admin.role}")
    print("\nYou can now login with:")
    print("  Username: admin")
    print("  Password: Admin@2026")
    print("=" * 60)
    
except CustomUser.DoesNotExist:
    print("Error: Admin1085 user not found!")
except Exception as e:
    print(f"Error: {e}")
