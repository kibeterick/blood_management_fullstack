#!/usr/bin/env python3
"""
Verify that the template files have the correct admin checks
"""

import os

def check_file(filepath, search_text):
    """Check if file contains the search text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return search_text in content
    except Exception as e:
        return f"Error: {e}"

print("=" * 70)
print("VERIFYING TEMPLATE FILES FOR ADMIN CHECKS")
print("=" * 70)

# Check donors_list.html
print("\n1. Checking donors_list.html...")
donors_file = "core_blood_system/templates/donors_list.html"
if check_file(donors_file, "{% if user.role == 'admin' %}"):
    print("   ✅ CORRECT: Admin check found in donors_list.html")
    if check_file(donors_file, "<th>Action</th>"):
        print("   ✅ CORRECT: Action column header found")
else:
    print("   ❌ ERROR: Admin check NOT found in donors_list.html")

# Check donation_request_list.html
print("\n2. Checking donation_request_list.html...")
donation_file = "core_blood_system/templates/donations/donation_request_list.html"
if check_file(donation_file, "{% if user.role == 'admin' %}"):
    print("   ✅ CORRECT: Admin check found in donation_request_list.html")
    if check_file(donation_file, "<th>Action</th>"):
        print("   ✅ CORRECT: Action column header found")
else:
    print("   ❌ ERROR: Admin check NOT found in donation_request_list.html")

print("\n" + "=" * 70)
print("CHECKING GIT STATUS")
print("=" * 70)

import subprocess

try:
    # Check current branch
    result = subprocess.run(['git', 'branch', '--show-current'], 
                          capture_output=True, text=True)
    print(f"\nCurrent branch: {result.stdout.strip()}")
    
    # Check last commit
    result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                          capture_output=True, text=True)
    print(f"Last commit: {result.stdout.strip()}")
    
    # Check if there are uncommitted changes
    result = subprocess.run(['git', 'status', '--short'], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print(f"\n⚠️  Uncommitted changes:\n{result.stdout}")
    else:
        print("\n✅ No uncommitted changes - all code is committed")
        
except Exception as e:
    print(f"Error checking git: {e}")

print("\n" + "=" * 70)
print("NEXT STEPS FOR PYTHONANYWHERE")
print("=" * 70)
print("""
If the files are correct here, but not working on PythonAnywhere:

1. CLEAR BROWSER CACHE:
   - Press Ctrl+Shift+Delete
   - Select "Cached images and files"
   - Click "Clear data"
   - OR just press Ctrl+Shift+R on the page

2. CHECK PYTHONANYWHERE PULLED CORRECTLY:
   Run this in PythonAnywhere console:
   
   cd /home/kibeterick/blood_management_fullstack
   git log -1 --oneline
   
   Should show: aba22ff Add comprehensive deployment guide

3. FORCE RELOAD PYTHONANYWHERE:
   Run this in PythonAnywhere console:
   
   touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
   
   Then click Reload button on web app page

4. CHECK WHICH USER YOU'RE LOGGED IN AS:
   - Make sure you're logged in as Kemei (regular user)
   - NOT as admin
   - Admin will always see Actions column
   - Regular users should NOT see Actions column

5. TRY INCOGNITO/PRIVATE BROWSING:
   - Open incognito window
   - Go to https://kibeterick.pythonanywhere.com
   - Login as Kemei
   - Check if Actions column is gone
""")

print("=" * 70)
