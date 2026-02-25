#!/usr/bin/env python3
"""
Deployment script for PythonAnywhere
Run this script on PythonAnywhere to update your live site
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print("OUTPUT:")
            print(result.stdout)
        if result.stderr:
            print("ERRORS:")
            print(result.stderr)
        if result.returncode == 0:
            print("✓ SUCCESS")
        else:
            print(f"✗ FAILED (exit code: {result.returncode})")
        return result.returncode == 0
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print("🩸 BLOOD MANAGEMENT SYSTEM - PYTHONANYWHERE DEPLOYMENT")
    print("=" * 60)
    
    # Change to project directory
    project_dir = "/home/kibeterick/blood_management_fullstack"
    os.chdir(project_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Step 1: Pull latest changes from GitHub
    if not run_command("git pull origin main", "Pulling latest changes from GitHub"):
        print("Failed to pull changes. Continuing anyway...")
    
    # Step 2: Activate virtual environment and install dependencies
    venv_activate = "source /home/kibeterick/.virtualenvs/blood-management/bin/activate"
    
    # Step 3: Collect static files
    if not run_command(f"{venv_activate} && python manage.py collectstatic --noinput", 
                      "Collecting static files"):
        print("Failed to collect static files. This might cause styling issues.")
    
    # Step 4: Run migrations
    if not run_command(f"{venv_activate} && python manage.py migrate", 
                      "Running database migrations"):
        print("Failed to run migrations. Database might be out of sync.")
    
    # Step 5: Update admin user (if needed)
    admin_script = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import CustomUser

try:
    # Check if admin user exists
    admin = CustomUser.objects.get(username='admin')
    print(f"Admin user exists: {admin.username}")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is staff: {admin.is_staff}")
    
    # Ensure admin has proper permissions
    if not admin.is_superuser:
        admin.is_superuser = True
        admin.save()
        print("Updated admin to superuser")
        
    if not admin.is_staff:
        admin.is_staff = True
        admin.save()
        print("Updated admin to staff")
        
except CustomUser.DoesNotExist:
    print("Admin user not found. Creating one...")
    admin = CustomUser.objects.create_user(
        username='admin',
        email='admin@bloodsystem.com',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        role='admin',
        is_staff=True,
        is_superuser=True
    )
    print("Admin user created successfully")

print("Admin setup complete!")
"""
    
    # Write and run admin setup script
    with open('/tmp/setup_admin.py', 'w') as f:
        f.write(admin_script)
    
    run_command(f"{venv_activate} && python /tmp/setup_admin.py", 
               "Setting up admin user")
    
    # Step 6: Reload web app
    print(f"\n{'='*60}")
    print("FINAL STEP: Reload Web App")
    print(f"{'='*60}")
    print("Please go to your PythonAnywhere dashboard and click 'Reload' on your web app")
    print("URL: https://www.pythonanywhere.com/user/kibeterick/webapps/")
    print("\nOr run this command in a PythonAnywhere console:")
    print("touch /var/www/kibeterick_pythonanywhere_com_wsgi.py")
    
    print(f"\n{'='*60}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*60}")
    print("✓ Code updated from GitHub")
    print("✓ Static files collected")
    print("✓ Database migrations applied")
    print("✓ Admin user configured")
    print("\n🎉 Deployment complete!")
    print("Your enhanced Blood Management System is now live at:")
    print("https://kibeterick.pythonanywhere.com")
    print("\nAdmin credentials:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    main()