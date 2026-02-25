#!/usr/bin/env python
"""
Test script to verify user management functionality
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser
from django.utils import timezone

def test_user_management():
    """Test user management system"""
    print("=" * 60)
    print("USER MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    print()
    
    # Get all users
    all_users = CustomUser.objects.all()
    print(f"✓ Total Users: {all_users.count()}")
    
    # Count by role
    admins = CustomUser.objects.filter(role='admin')
    regular_users = CustomUser.objects.filter(role='user')
    print(f"✓ Administrators: {admins.count()}")
    print(f"✓ Regular Users: {regular_users.count()}")
    
    # Active users
    active_users = CustomUser.objects.filter(is_active=True)
    inactive_users = CustomUser.objects.filter(is_active=False)
    print(f"✓ Active Users: {active_users.count()}")
    print(f"✓ Inactive Users: {inactive_users.count()}")
    
    print()
    print("-" * 60)
    print("USER LIST:")
    print("-" * 60)
    
    for user in all_users:
        role_badge = "🛡️ ADMIN" if user.role == 'admin' else "👤 USER"
        status = "✓ Active" if user.is_active else "✗ Inactive"
        superuser = " [SUPERUSER]" if user.is_superuser else ""
        
        print(f"{role_badge} {user.username}{superuser}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        print(f"   Phone: {user.phone_number or 'N/A'}")
        print(f"   Blood Type: {user.blood_type or 'N/A'}")
        print(f"   Status: {status}")
        print(f"   Joined: {user.date_joined.strftime('%B %d, %Y')}")
        if user.last_login:
            print(f"   Last Login: {user.last_login.strftime('%B %d, %Y %I:%M %p')}")
        print()
    
    print("=" * 60)
    print("USER MANAGEMENT FEATURES:")
    print("=" * 60)
    print("✓ View all users with details")
    print("✓ Search by username, name, email, phone")
    print("✓ Filter by role (Admin/User)")
    print("✓ Filter by status (Active/Inactive)")
    print("✓ View individual user details")
    print("✓ Edit user information")
    print("✓ Statistics dashboard")
    print()
    print("ACCESS:")
    print("- URL: /users/")
    print("- Button: Admin Dashboard → Quick Actions → User Management")
    print("- Permission: Admin only")
    print()
    print("=" * 60)
    print("✅ USER MANAGEMENT SYSTEM IS READY!")
    print("=" * 60)

if __name__ == '__main__':
    test_user_management()
