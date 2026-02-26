#!/usr/bin/env python
"""
Diagnostic script to check admin user and dashboard routing
Run this on PythonAnywhere to diagnose the issue
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

print("=" * 60)
print("ADMIN USER DIAGNOSTIC")
print("=" * 60)

# Check admin user
try:
    admin = CustomUser.objects.get(username='admin')
    print(f"\n✓ Admin user found:")
    print(f"  - Username: {admin.username}")
    print(f"  - Role: {admin.role}")
    print(f"  - Is Staff: {admin.is_staff}")
    print(f"  - Is Superuser: {admin.is_superuser}")
    print(f"  - Is Active: {admin.is_active}")
    print(f"  - First Name: {admin.first_name}")
    print(f"  - Last Name: {admin.last_name}")
    print(f"  - Email: {admin.email}")
    
    # Check if role is exactly 'admin'
    if admin.role == 'admin':
        print(f"\n✓ Role is correctly set to 'admin'")
    else:
        print(f"\n✗ WARNING: Role is '{admin.role}' not 'admin'")
        print(f"  Fixing role now...")
        admin.role = 'admin'
        admin.save()
        print(f"  ✓ Role fixed to 'admin'")
    
    # Check all users
    print(f"\n" + "=" * 60)
    print("ALL USERS IN SYSTEM")
    print("=" * 60)
    all_users = CustomUser.objects.all()
    print(f"\nTotal users: {all_users.count()}")
    for user in all_users:
        print(f"\n  User: {user.username}")
        print(f"    - Role: {user.role}")
        print(f"    - Name: {user.first_name} {user.last_name}")
        print(f"    - Email: {user.email}")
        print(f"    - Is Staff: {user.is_staff}")
        print(f"    - Is Active: {user.is_active}")
    
except CustomUser.DoesNotExist:
    print("\n✗ Admin user 'admin' not found!")
    print("  Creating admin user now...")
    admin = CustomUser.objects.create_user(
        username='admin',
        password='E38736434k',
        role='admin',
        is_staff=True,
        is_superuser=True,
        first_name='System',
        last_name='Administrator',
        email='admin@bloodsystem.com'
    )
    print(f"  ✓ Admin user created successfully")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
