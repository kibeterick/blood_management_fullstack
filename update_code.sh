#!/bin/bash
cd /home/kibeterick/blood_management_fullstack
git pull origin main
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py
echo "Code updated successfully! Now reload your web app."
