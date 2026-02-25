#!/usr/bin/env python
"""
Delete Admin254 user
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

try:
    # Get the user
    user = CustomUser.objects.get(username='Admin254')
    
    print("=" * 60)
    print("USER TO DELETE")
    print("=" * 60)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Role: {user.role}")
    
    # Delete the user
    user.delete()
    
    print("\n✓ User 'Admin254' has been deleted successfully!")
    print("=" * 60)
    
except CustomUser.DoesNotExist:
    print("User 'Admin254' not found!")
except Exception as e:
    print(f"Error: {e}")
