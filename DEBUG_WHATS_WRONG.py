#!/usr/bin/env python3
"""
Debug script to check what's actually on PythonAnywhere
Run this on PythonAnywhere console to see what's missing
"""

import os
import subprocess

print("=" * 70)
print("🔍 DEBUGGING: Why can't you see the usability features?")
print("=" * 70)

# Check current commit
print("\n1. CHECKING CURRENT COMMIT:")
print("-" * 70)
result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
print(f"Current commit: {result.stdout.strip()}")
print(f"Expected: 4afdd0e or later")

# Check if usability files exist
print("\n2. CHECKING IF USABILITY FILES EXIST:")
print("-" * 70)

files_to_check = [
    'core_blood_system/static/js/usability.js',
    'core_blood_system/static/css/password-toggle.css',
    'core_blood_system/templates/help_widget.html',
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"{status}: {file_path}")

# Check if static files were collected
print("\n3. CHECKING STATIC FILES COLLECTION:")
print("-" * 70)

static_files = [
    'staticfiles/js/usability.js',
    'staticfiles/css/password-toggle.css',
]

for file_path in static_files:
    exists = os.path.exists(file_path)
    status = "✅ COLLECTED" if exists else "❌ NOT COLLECTED"
    print(f"{status}: {file_path}")

# Check login.html for password toggle script
print("\n4. CHECKING LOGIN.HTML FOR PASSWORD TOGGLE:")
print("-" * 70)

login_file = 'core_blood_system/templates/login.html'
if os.path.exists(login_file):
    with open(login_file, 'r') as f:
        content = f.read()
        has_bootstrap_icons = 'bootstrap-icons' in content
        has_password_script = 'Password Toggle Script' in content
        has_eye_icon = 'bi-eye' in content
        
        print(f"✅ File exists: {login_file}")
        print(f"{'✅' if has_bootstrap_icons else '❌'} Bootstrap Icons included")
        print(f"{'✅' if has_password_script else '❌'} Password toggle script present")
        print(f"{'✅' if has_eye_icon else '❌'} Eye icon code present")
else:
    print(f"❌ File missing: {login_file}")

# Check base.html for usability scripts
print("\n5. CHECKING BASE.HTML FOR USABILITY SCRIPTS:")
print("-" * 70)

base_file = 'core_blood_system/templates/base.html'
if os.path.exists(base_file):
    with open(base_file, 'r') as f:
        content = f.read()
        has_usability_js = 'usability.js' in content
        has_password_css = 'password-toggle.css' in content
        has_help_widget = 'help_widget.html' in content
        
        print(f"✅ File exists: {base_file}")
        print(f"{'✅' if has_usability_js else '❌'} usability.js included")
        print(f"{'✅' if has_password_css else '❌'} password-toggle.css included")
        print(f"{'✅' if has_help_widget else '❌'} help_widget.html included")
else:
    print(f"❌ File missing: {base_file}")

# Check web server reload
print("\n6. CHECKING WEB SERVER STATUS:")
print("-" * 70)
print("⚠️  Did you run: touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
print("⚠️  This reloads the web server to pick up new files")

# Summary
print("\n" + "=" * 70)
print("📋 SUMMARY & NEXT STEPS:")
print("=" * 70)

print("\nIf files are MISSING:")
print("  → Run: git pull origin main")
print("  → Run: python manage.py collectstatic --noinput")

print("\nIf files EXIST but not COLLECTED:")
print("  → Run: python manage.py collectstatic --clear --noinput")

print("\nIf files EXIST and COLLECTED:")
print("  → Run: touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
print("  → Hard refresh browser: Ctrl + Shift + R")
print("  → Try incognito mode")
print("  → Clear browser cache completely")

print("\n" + "=" * 70)
