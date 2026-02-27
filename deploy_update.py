#!/usr/bin/env python3
"""
Deploy script to update code from GitHub on PythonAnywhere
Upload this file to PythonAnywhere and run it from the Files interface
"""

import os
import subprocess

print("=" * 60)
print("DEPLOYING CODE UPDATE FROM GITHUB")
print("=" * 60)

# Change to project directory
project_dir = '/home/kibeterick/blood_management_fullstack'
os.chdir(project_dir)
print(f"\n✓ Changed to directory: {project_dir}")

# Fetch latest code from GitHub
print("\n1. Fetching latest code from GitHub...")
result = subprocess.run(['git', 'fetch', 'origin'], capture_output=True, text=True)
print(result.stdout)
if result.returncode == 0:
    print("✓ Fetch successful")
else:
    print(f"✗ Error: {result.stderr}")

# Reset to match GitHub
print("\n2. Resetting to match GitHub main branch...")
result = subprocess.run(['git', 'reset', '--hard', 'origin/main'], capture_output=True, text=True)
print(result.stdout)
if result.returncode == 0:
    print("✓ Reset successful")
else:
    print(f"✗ Error: {result.stderr}")

# Touch WSGI file to reload app
print("\n3. Triggering app reload...")
wsgi_file = '/var/www/kibeterick_pythonanywhere_com_wsgi.py'
subprocess.run(['touch', wsgi_file])
print(f"✓ Touched {wsgi_file}")

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE!")
print("=" * 60)
print("\nNext steps:")
print("1. Go to Web tab: https://www.pythonanywhere.com/user/kibeterick/webapps/")
print("2. Click the green 'Reload' button")
print("3. Visit your site and press Ctrl+Shift+R to refresh")
print("\nThe Admin dropdown should now be visible!")
