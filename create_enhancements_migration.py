#!/usr/bin/env python
"""
Create database migrations for the 5 new enhancement features
Run this script to generate migrations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

print("=" * 60)
print("CREATING MIGRATIONS FOR TOP 5 ENHANCEMENTS")
print("=" * 60)
print()
print("New Models:")
print("1. DonationAppointment - Appointment scheduling")
print("2. Notification - Real-time notifications")
print("3. MatchedDonor - Blood request matching")
print("4. QRCode - QR code system")
print()
print("Creating migrations...")
print()

try:
    # Create migrations
    call_command('makemigrations', 'core_blood_system')
    print()
    print("✅ Migrations created successfully!")
    print()
    print("Next steps:")
    print("1. Review the migration file in core_blood_system/migrations/")
    print("2. Run: python manage.py migrate")
    print("3. Install required package: pip install qrcode[pil]")
    print()
except Exception as e:
    print(f"❌ Error creating migrations: {str(e)}")
    sys.exit(1)
