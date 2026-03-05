"""
Backend package initialization
Ensures Celery app is loaded when Django starts
"""

# Celery import commented out - not installed on PythonAnywhere
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# from core_blood_system.celery import app as celery_app

# __all__ = ('celery_app',)
