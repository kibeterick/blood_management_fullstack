#!/usr/bin/env python
"""
Force create migrations for enhancement models
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command

print("=" * 60)
print("FORCING MIGRATION CREATION")
print("=" * 60)

# Try to create migrations
try:
    call_command('makemigrations', 'core_blood_system', '--empty', '--name', 'add_enhancement_models')
    print("\n✅ Empty migration created!")
    print("\nNow manually edit the migration file to add the models.")
except Exception as e:
    print(f"❌ Error: {e}")
    
print("\nAlternatively, try:")
print("python manage.py makemigrations core_blood_system --verbosity 3")
