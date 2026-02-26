#!/bin/bash
# Deploy admin dashboard redirect fix to PythonAnywhere

echo "=========================================="
echo "DEPLOYING ADMIN DASHBOARD FIX"
echo "=========================================="

# Navigate to project directory
cd ~/blood_management_fullstack

# Activate virtual environment
source venv/bin/activate

# Pull latest code from GitHub
echo ""
echo "1. Pulling latest code from GitHub..."
git pull origin main

# Run diagnostic and fix script
echo ""
echo "2. Running admin user diagnostic and fix..."
python fix_admin_dashboard_redirect.py

# Collect static files
echo ""
echo "3. Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run system check
echo ""
echo "4. Running Django system check..."
python manage.py check

# Touch WSGI file to reload
echo ""
echo "5. Reloading web app..."
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Log out from https://kibeterick.pythonanywhere.com"
echo "2. Clear your browser cache (Ctrl+Shift+Delete)"
echo "3. Close all browser tabs"
echo "4. Open a new browser window"
echo "5. Go to https://kibeterick.pythonanywhere.com"
echo "6. Log in with username: admin, password: E38736434k"
echo "7. You should now see the admin dashboard with:"
echo "   - Blood Inventory with animated blood bags"
echo "   - Registered Users table"
echo "   - All admin features"
echo ""
echo "If you still see the user dashboard:"
echo "- Try a different browser (Chrome, Firefox, Edge)"
echo "- Try incognito/private browsing mode"
echo "- Check that you're going to /admin-dashboard/ URL"
echo "=========================================="
