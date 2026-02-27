#!/bin/bash
# Run this script on PythonAnywhere console to check deployment status

echo "=========================================="
echo "CHECKING PYTHONANYWHERE DEPLOYMENT"
echo "=========================================="

cd /home/kibeterick/blood_management_fullstack

echo ""
echo "1. Current Git Commit:"
git log -1 --oneline

echo ""
echo "2. Checking donors_list.html for admin check:"
grep -n "{% if user.role == 'admin' %}" core_blood_system/templates/donors_list.html | head -5

echo ""
echo "3. Checking donation_request_list.html for admin check:"
grep -n "{% if user.role == 'admin' %}" core_blood_system/templates/donations/donation_request_list.html | head -5

echo ""
echo "=========================================="
echo "EXPECTED RESULTS:"
echo "=========================================="
echo "Git commit should be: aba22ff"
echo "Should see multiple lines with admin checks"
echo ""
echo "If you DON'T see these, run:"
echo "git pull origin main"
echo "touch /var/www/kibeterick_pythonanywhere_com_wsgi.py"
echo "=========================================="
