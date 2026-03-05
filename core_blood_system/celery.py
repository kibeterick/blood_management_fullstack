"""
Celery Configuration for Blood Management System
Handles scheduled tasks for notifications and inventory management
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('blood_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure scheduled tasks
app.conf.beat_schedule = {
    'send-appointment-reminders-daily': {
        'task': 'core_blood_system.tasks.send_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9:00 AM
    },
    'mark-expired-blood-units-daily': {
        'task': 'core_blood_system.tasks.mark_expired_units',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'check-low-stock-daily': {
        'task': 'core_blood_system.tasks.check_low_stock',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
