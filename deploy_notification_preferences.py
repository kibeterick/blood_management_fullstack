#!/usr/bin/env python3
"""
Deploy Notification Preferences to PythonAnywhere
This script helps you deploy the notification preferences feature
"""

import os
import shutil
from pathlib import Path

def find_django_project():
    """Find the Django project directory"""
    home = Path.home()
    print(f"Searching for Django project in {home}...")
    
    # Common project locations
    possible_locations = [
        home / "blooddonation",
        home / "BloodDonationSystem",
        home / "mysite",
        home / "django_project",
    ]
    
    # Search for manage.py
    for location in possible_locations:
        if location.exists() and (location / "manage.py").exists():
            print(f"✓ Found Django project at: {location}")
            return location
    
    # If not found in common locations, search recursively
    print("Searching recursively (this may take a moment)...")
    for path in home.rglob("manage.py"):
        if path.is_file():
            project_dir = path.parent
            print(f"✓ Found Django project at: {project_dir}")
            return project_dir
    
    return None

def deploy_notification_preferences(project_dir):
    """Deploy the notification preferences files"""
    
    # Define source and destination paths
    template_dest = project_dir / "core_blood_system" / "templates" / "notifications" / "notification_preferences.html"
    
    print("\n" + "="*60)
    print("DEPLOYMENT STATUS")
    print("="*60)
    
    # Check if template directory exists
    template_dir = template_dest.parent
    if not template_dir.exists():
        print(f"✗ Template directory doesn't exist: {template_dir}")
        print(f"  Creating directory...")
        template_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory created")
    
    # Check if files need to be created
    files_to_check = {
        "Template": template_dest,
        "URLs": project_dir / "core_blood_system" / "urls.py",
        "Views": project_dir / "core_blood_system" / "views.py",
        "Dashboard": project_dir / "core_blood_system" / "templates" / "dashboard" / "user_dashboard_enhanced.html",
    }
    
    print("\nFile Status:")
    for name, path in files_to_check.items():
        if path.exists():
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: NOT FOUND - {path}")
    
    return project_dir

def main():
    print("="*60)
    print("NOTIFICATION PREFERENCES DEPLOYMENT SCRIPT")
    print("="*60)
    
    # Find project
    project_dir = find_django_project()
    
    if not project_dir:
        print("\n✗ Could not find Django project!")
        print("\nPlease run this command manually to find your project:")
        print("  find ~ -name 'manage.py' -type f 2>/dev/null")
        return
    
    # Deploy files
    deploy_notification_preferences(project_dir)
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. If using Git, pull latest changes:")
    print(f"   cd {project_dir}")
    print("   git pull origin main")
    print("\n2. Reload your web app:")
    print("   - Go to PythonAnywhere Web tab")
    print("   - Click the green 'Reload' button")
    print("\n3. Test the feature:")
    print("   - Log into your site")
    print("   - Go to dashboard")
    print("   - Click 'Notification Settings' (🔔 icon)")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
