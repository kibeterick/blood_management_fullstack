#!/usr/bin/env python
"""
Test if new models can be imported
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("Testing model imports...")
print("=" * 60)

try:
    from core_blood_system.models import DonationAppointment
    print("✅ DonationAppointment imported successfully")
    print(f"   Fields: {[f.name for f in DonationAppointment._meta.fields]}")
except Exception as e:
    print(f"❌ DonationAppointment import failed: {e}")

try:
    from core_blood_system.models import Notification
    print("✅ Notification imported successfully")
    print(f"   Fields: {[f.name for f in Notification._meta.fields]}")
except Exception as e:
    print(f"❌ Notification import failed: {e}")

try:
    from core_blood_system.models import MatchedDonor
    print("✅ MatchedDonor imported successfully")
    print(f"   Fields: {[f.name for f in MatchedDonor._meta.fields]}")
except Exception as e:
    print(f"❌ MatchedDonor import failed: {e}")

try:
    from core_blood_system.models import QRCode
    print("✅ QRCode imported successfully")
    print(f"   Fields: {[f.name for f in QRCode._meta.fields]}")
except Exception as e:
    print(f"❌ QRCode import failed: {e}")

print("=" * 60)
print("\nIf all models imported successfully, try:")
print("python manage.py makemigrations core_blood_system --dry-run")
print("\nThen:")
print("python manage.py makemigrations core_blood_system")
