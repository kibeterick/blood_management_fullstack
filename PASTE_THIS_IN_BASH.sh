#!/bin/bash
# Copy and paste this entire code block into PythonAnywhere bash console

cd /home/kibeterick/blood_management_fullstack && \
git pull origin main && \
python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('Cache cleared')" && \
touch /var/www/kibeterick_pythonanywhere_com_wsgi.py && \
echo "Done! Now go to Web tab and click Reload button"
