#!/usr/bin/env python
"""
Fix admin dashboard redirect issue
This script will verify and fix the admin user's role
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

print("=" * 60)
print("FIXING ADMIN DASHBOARD REDIRECT")
print("=" * 60)

# Get admin user
try:
    admin = CustomUser.objects.get(username='admin')
    print(f"\n✓ Found admin user: {admin.username}")
    print(f"  Current role: '{admin.role}'")
    print(f"  Role type: {type(admin.role)}")
    print(f"  Role repr: {repr(admin.role)}")
    
    # Force set role to 'admin' (no spaces, lowercase)
    admin.role = 'admin'
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.save()
    
    print(f"\n✓ Admin user updated:")
    print(f"  - Role: {admin.role}")
    print(f"  - Is Staff: {admin.is_staff}")
    print(f"  - Is Superuser: {admin.is_superuser}")
    print(f"  - Is Active: {admin.is_active}")
    
    # Verify the change
    admin.refresh_from_db()
    print(f"\n✓ Verified from database:")
    print(f"  - Role: '{admin.role}'")
    
    if admin.role == 'admin':
        print(f"\n✓✓✓ SUCCESS! Admin role is correctly set to 'admin'")
    else:
        print(f"\n✗✗✗ ERROR! Role is still '{admin.role}'")
        
except CustomUser.DoesNotExist:
    print("\n✗ Admin user not found!")
    print("  Creating new admin user...")
    admin = CustomUser.objects.create_user(
        username='admin',
        password='E38736434k',
        role='admin',
        is_staff=True,
        is_superuser=True,
        is_active=True,
        first_name='System',
        last_name='Administrator',
        email='admin@bloodsystem.com'
    )
    print(f"✓ Admin user created successfully")

print("\n" + "=" * 60)
print("FIX COMPLETE - Please log out and log back in")
print("=" * 60)
