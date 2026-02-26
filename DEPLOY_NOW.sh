#!/bin/bash
# Quick deployment script for PythonAnywhere

echo "=========================================="
echo "DEPLOYING WELCOME MODAL FIX"
echo "=========================================="

cd ~/blood_management_fullstack
source venv/bin/activate

echo "Pulling latest changes from GitHub..."
git pull origin main

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Reloading web app..."
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py

echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Now test:"
echo "1. Logout from your account"
echo "2. Login again"
echo "3. Click 'Let's Get Started'"
echo "4. Modal should close smoothly!"
echo ""
