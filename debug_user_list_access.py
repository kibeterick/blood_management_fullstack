#!/usr/bin/env python
"""
Debug script to check user list access issues
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser
from django.contrib.auth import get_user_model

def debug_user_list():
    """Debug user list access"""
    print("=" * 60)
    print("USER LIST ACCESS DIAGNOSTIC")
    print("=" * 60)
    print()
    
    # Check admin user
    try:
        admin = CustomUser.objects.get(username='admin')
        print("✓ Admin user found:")
        print(f"  Username: {admin.username}")
        print(f"  Role: {admin.role}")
        print(f"  Is Staff: {admin.is_staff}")
        print(f"  Is Superuser: {admin.is_superuser}")
        print(f"  Is Active: {admin.is_active}")
        print()
        
        # Check if role is exactly 'admin'
        if admin.role == 'admin':
            print("✓ Admin role is correctly set to 'admin'")
        else:
            print(f"✗ WARNING: Admin role is '{admin.role}' (should be 'admin')")
            print("  Fixing now...")
            admin.role = 'admin'
            admin.save()
            print("  ✓ Fixed! Role set to 'admin'")
        print()
        
    except CustomUser.DoesNotExist:
        print("✗ ERROR: Admin user not found!")
        return
    
    # Check URL configuration
    print("URL Configuration Check:")
    print("  User List URL: /users/")
    print("  Expected URL name: 'user_list'")
    print()
    
    # Check template location
    import os
    template_path = "core_blood_system/templates/users/user_list.html"
    if os.path.exists(template_path):
        print(f"✓ Template exists: {template_path}")
    else:
        print(f"✗ Template NOT found: {template_path}")
    print()
    
    # Check all users
    all_users = CustomUser.objects.all()
    print(f"Total users in database: {all_users.count()}")
    print()
    
    # Test the view logic
    print("Testing View Logic:")
    print("-" * 60)
    
    # Simulate the view's permission check
    if admin.role != 'admin':
        print("✗ ISSUE FOUND: Admin role check would FAIL")
        print(f"  Current role: '{admin.role}'")
        print(f"  Expected: 'admin'")
    else:
        print("✓ Permission check would PASS")
        print(f"  Admin role: '{admin.role}' == 'admin'")
    print()
    
    # Check if there are users to display
    if all_users.count() > 0:
        print(f"✓ Users available to display: {all_users.count()}")
        print()
        print("Users that would be shown:")
        for i, user in enumerate(all_users[:5], 1):
            print(f"  {i}. {user.username} ({user.role}) - {user.email}")
        if all_users.count() > 5:
            print(f"  ... and {all_users.count() - 5} more")
    else:
        print("✗ No users in database!")
    print()
    
    print("=" * 60)
    print("TROUBLESHOOTING STEPS:")
    print("=" * 60)
    print()
    print("1. Make sure you're logged in as 'admin'")
    print("2. Go to: http://127.0.0.1:8000/users/")
    print("3. Or click 'User Management' button on admin dashboard")
    print()
    print("If you see an error, check:")
    print("- Browser console for JavaScript errors")
    print("- Django server console for Python errors")
    print("- Make sure server is running: python manage.py runserver")
    print()
    
    # Create a quick access test
    print("=" * 60)
    print("QUICK ACCESS TEST")
    print("=" * 60)
    print()
    print("Run this in your browser console to test the link:")
    print("  window.location.href = '/users/';")
    print()
    print("Or try this direct link:")
    print("  http://127.0.0.1:8000/users/")
    print()

if __name__ == '__main__':
    debug_user_list()
