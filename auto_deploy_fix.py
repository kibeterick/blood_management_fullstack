#!/usr/bin/env python3
"""
Auto-deploy script for PythonAnywhere
Run this in PythonAnywhere bash console: python auto_deploy_fix.py
"""
import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        print(f"✓ {cmd}")
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("DEPLOYING FIX TO PYTHONANYWHERE")
    print("=" * 60)
    
    # Project directory
    project_dir = "/home/kibeterick/blood_management_fullstack"
    
    # Check if directory exists
    if not os.path.exists(project_dir):
        print(f"✗ Project directory not found: {project_dir}")
        sys.exit(1)
    
    print(f"\n1. Navigating to project directory...")
    os.chdir(project_dir)
    print(f"   Current directory: {os.getcwd()}")
    
    print(f"\n2. Pulling latest code from GitHub...")
    if not run_command("git pull origin main", cwd=project_dir):
        print("✗ Git pull failed!")
        sys.exit(1)
    
    print(f"\n3. Touching WSGI file to trigger reload...")
    wsgi_file = "/var/www/kibeterick_pythonanywhere_com_wsgi.py"
    if not run_command(f"touch {wsgi_file}"):
        print("✗ Failed to touch WSGI file!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click the green 'Reload' button")
    print("3. Test your site - go to 'My Appointments'")
    print("\nFIXED: Template syntax error in my_appointments.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
