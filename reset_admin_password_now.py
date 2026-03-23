"""
Reset Admin Password Script
Run this with: python reset_admin_password_now.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Find admin user
admin = User.objects.filter(is_superuser=True).first()

if admin:
    # Set new password
    new_password = "admin123"
    admin.set_password(new_password)
    admin.save()
    
    print("=" * 50)
    print("ADMIN PASSWORD RESET SUCCESSFUL!")
    print("=" * 50)
    print(f"Username: {admin.username}")
    print(f"Password: {new_password}")
    print("=" * 50)
    print("\nLogin at: http://127.0.0.1:8000/admin/")
    print("=" * 50)
else:
    print("No admin user found. Creating new admin...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@bloodbank.com',
        password='admin123'
    )
    print("=" * 50)
    print("NEW ADMIN CREATED!")
    print("=" * 50)
    print(f"Username: admin")
    print(f"Password: admin123")
    print("=" * 50)
    print("\nLogin at: http://127.0.0.1:8000/admin/")
    print("=" * 50)
