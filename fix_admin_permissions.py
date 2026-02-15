"""
Script to fix admin permissions for existing users
Run this with: python fix_admin_permissions.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

# Get the user by username
username = input("Enter username to make admin (e.g., Admin254): ")

try:
    user = CustomUser.objects.get(username=username)
    
    # Set admin permissions
    user.is_staff = True
    user.is_superuser = True
    user.role = 'admin'
    user.save()
    
    print(f"\n✅ SUCCESS! User '{username}' now has full admin permissions:")
    print(f"   - is_staff: {user.is_staff}")
    print(f"   - is_superuser: {user.is_superuser}")
    print(f"   - role: {user.role}")
    print(f"\nYou can now access Django admin at: http://127.0.0.1:8000/admin/")
    
except CustomUser.DoesNotExist:
    print(f"\n❌ ERROR: User '{username}' not found!")
    print("\nAvailable users:")
    for u in CustomUser.objects.all():
        print(f"   - {u.username} (role: {u.role}, staff: {u.is_staff}, superuser: {u.is_superuser})")
