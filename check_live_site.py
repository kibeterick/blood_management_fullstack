#!/usr/bin/env python3
"""
Check what's actually being served on the live site
"""

import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("🔍 CHECKING LIVE SITE: What is actually being served?")
print("=" * 70)

url = "https://kibeterick.pythonanywhere.com/login/"

try:
    print(f"\nFetching: {url}")
    response = requests.get(url, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        html = response.text
        
        # Check for key components
        checks = {
            'Bootstrap Icons CDN': 'bootstrap-icons' in html,
            'Password Toggle Script': 'Password Toggle Script' in html,
            'Eye icon (bi-eye)': 'bi-eye' in html,
            'Eye slash icon': 'bi-eye-slash' in html,
            'Toggle button': 'toggleBtn' in html,
        }
        
        print("\n📋 CHECKING LIVE PAGE FOR PASSWORD TOGGLE:")
        print("-" * 70)
        
        all_present = True
        for check_name, is_present in checks.items():
            status = "✅" if is_present else "❌"
            print(f"{status} {check_name}")
            if not is_present:
                all_present = False
        
        print("\n" + "=" * 70)
        
        if all_present:
            print("✅ The live site HAS the password toggle code!")
            print("\nThe problem is 100% browser cache.")
            print("\nTry these in order:")
            print("1. Close ALL browser tabs")
            print("2. Clear browser cache completely")
            print("3. Restart browser")
            print("4. Try incognito mode")
            print("5. Try different browser")
        else:
            print("❌ The live site DOES NOT have the password toggle code!")
            print("\nPythonAnywhere might be caching the old template.")
            print("\nRun this on PythonAnywhere:")
            print("  touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
            print("  Wait 30 seconds, then try again")
        
        # Show a snippet of the password field
        if '<input type="password"' in html:
            print("\n📄 PASSWORD FIELD HTML FROM LIVE SITE:")
            print("-" * 70)
            soup = BeautifulSoup(html, 'html.parser')
            password_inputs = soup.find_all('input', {'type': 'password'})
            if password_inputs:
                # Show the parent div
                for pwd_input in password_inputs[:1]:  # Just first one
                    parent = pwd_input.parent
                    print(str(parent)[:300])  # First 300 chars
            print("-" * 70)
        
    else:
        print(f"❌ Error: Got status code {response.status_code}")
        
except Exception as e:
    print(f"❌ Error fetching page: {e}")
    print("\nMake sure you have requests and beautifulsoup4 installed:")
    print("  pip install requests beautifulsoup4")

print("=" * 70)
