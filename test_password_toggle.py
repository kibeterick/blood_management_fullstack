#!/usr/bin/env python3
"""
Quick test to verify password toggle is in login.html
Run this on PythonAnywhere to check if the file has the eye icon code
"""

import os

print("=" * 70)
print("🔍 TESTING: Does login.html have password toggle?")
print("=" * 70)

login_file = 'core_blood_system/templates/login.html'

if not os.path.exists(login_file):
    print(f"\n❌ ERROR: {login_file} does not exist!")
    print("You need to run: git pull origin main")
    exit(1)

print(f"\n✅ File exists: {login_file}")

# Read the file
with open(login_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check for key components
checks = {
    'Bootstrap Icons CDN': 'bootstrap-icons@1.11.0' in content,
    'Password Toggle Script comment': '<!-- Password Toggle Script -->' in content,
    'Eye icon (bi-eye)': 'bi-eye' in content,
    'Eye slash icon (bi-eye-slash)': 'bi-eye-slash' in content,
    'Toggle button creation': 'toggleBtn.addEventListener' in content,
    'Password field wrapper': 'wrapper.appendChild' in content,
}

print("\n📋 CHECKING FOR PASSWORD TOGGLE COMPONENTS:")
print("-" * 70)

all_present = True
for check_name, is_present in checks.items():
    status = "✅" if is_present else "❌"
    print(f"{status} {check_name}")
    if not is_present:
        all_present = False

print("\n" + "=" * 70)

if all_present:
    print("✅ SUCCESS: Password toggle code IS present in login.html")
    print("\nThe file has all the necessary code for the eye icon.")
    print("\nIf you still don't see it in your browser:")
    print("1. Run: python manage.py collectstatic --clear --noinput")
    print("2. Run: touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
    print("3. Clear your browser cache (Ctrl + Shift + R)")
    print("4. Try incognito mode")
else:
    print("❌ PROBLEM: Password toggle code is MISSING from login.html")
    print("\nYou need to pull the latest code:")
    print("1. Run: git fetch origin")
    print("2. Run: git reset --hard origin/main")
    print("3. Run: git log --oneline -1")
    print("   (Should show: 4afdd0e or later)")

print("=" * 70)

# Show a snippet of the password field HTML
print("\n📄 SAMPLE OF PASSWORD FIELD HTML:")
print("-" * 70)

# Find the password field section
if '<input type="password"' in content:
    # Find the section around the password field
    password_index = content.find('<input type="password"')
    start = max(0, password_index - 200)
    end = min(len(content), password_index + 200)
    snippet = content[start:end]
    
    # Show just a few lines
    lines = snippet.split('\n')
    for line in lines[-5:]:
        if line.strip():
            print(line[:80])  # First 80 chars
else:
    print("❌ Could not find password field in HTML")

print("-" * 70)
