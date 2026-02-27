#!/usr/bin/env python
"""
Create migration for advanced security features
Run this script to generate the migration file
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

print("Creating migration for advanced security features...")
call_command('makemigrations', 'core_blood_system')
print("✅ Migration created successfully!")
print("\nNext steps:")
print("1. Review the migration file in core_blood_system/migrations/")
print("2. Run: python manage.py migrate")
print("3. Restart your Django server")
