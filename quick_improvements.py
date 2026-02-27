#!/usr/bin/env python3
"""
Quick System Improvements - Can be applied immediately
Run this script to add database indexes and optimize queries
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def add_database_indexes():
    """Add indexes to improve query performance"""
    print("=" * 60)
    print("ADDING DATABASE INDEXES FOR PERFORMANCE")
    print("=" * 60)
    
    indexes = [
        # Donor indexes
        "CREATE INDEX IF NOT EXISTS idx_donor_blood_type ON core_blood_system_donor(blood_type);",
        "CREATE INDEX IF NOT EXISTS idx_donor_available ON core_blood_system_donor(is_available);",
        "CREATE INDEX IF NOT EXISTS idx_donor_city ON core_blood_system_donor(city);",
        "CREATE INDEX IF NOT EXISTS idx_donor_blood_city ON core_blood_system_donor(blood_type, city);",
        
        # BloodRequest indexes
        "CREATE INDEX IF NOT EXISTS idx_request_blood_type ON core_blood_system_bloodrequest(blood_type);",
        "CREATE INDEX IF NOT EXISTS idx_request_status ON core_blood_system_bloodrequest(status);",
        "CREATE INDEX IF NOT EXISTS idx_request_urgency ON core_blood_system_bloodrequest(urgency);",
        "CREATE INDEX IF NOT EXISTS idx_request_date ON core_blood_system_bloodrequest(required_date);",
        
        # BloodDonation indexes
        "CREATE INDEX IF NOT EXISTS idx_donation_blood_type ON core_blood_system_blooddonation(blood_type);",
        "CREATE INDEX IF NOT EXISTS idx_donation_status ON core_blood_system_blooddonation(status);",
        "CREATE INDEX IF NOT EXISTS idx_donation_date ON core_blood_system_blooddonation(donation_date);",
        
        # CustomUser indexes
        "CREATE INDEX IF NOT EXISTS idx_user_role ON core_blood_system_customuser(role);",
        "CREATE INDEX IF NOT EXISTS idx_user_blood_type ON core_blood_system_customuser(blood_type);",
    ]
    
    with connection.cursor() as cursor:
        for idx, sql in enumerate(indexes, 1):
            try:
                print(f"\n[{idx}/{len(indexes)}] Creating index...")
                cursor.execute(sql)
                print(f"✅ Success: {sql[:60]}...")
            except Exception as e:
                print(f"⚠️  Warning: {str(e)[:80]}")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE INDEXES ADDED SUCCESSFULLY")
    print("=" * 60)


def analyze_slow_queries():
    """Analyze and report slow queries"""
    print("\n" + "=" * 60)
    print("ANALYZING DATABASE QUERIES")
    print("=" * 60)
    
    from django.db import reset_queries
    from django.conf import settings
    
    # Enable query logging temporarily
    settings.DEBUG = True
    reset_queries()
    
    # Import models
    from core_blood_system.models import Donor, BloodRequest, BloodDonation
    
    # Test common queries
    queries_to_test = [
        ("All available donors", lambda: list(Donor.objects.filter(is_available=True))),
        ("Donors by blood type", lambda: list(Donor.objects.filter(blood_type='O+'))),
        ("Pending requests", lambda: list(BloodRequest.objects.filter(status='pending'))),
        ("Recent donations", lambda: list(BloodDonation.objects.all()[:10])),
    ]
    
    print("\nQuery Performance Analysis:")
    print("-" * 60)
    
    for name, query_func in queries_to_test:
        reset_queries()
        query_func()
        
        from django.db import connection
        num_queries = len(connection.queries)
        
        print(f"\n{name}:")
        print(f"  Queries executed: {num_queries}")
        
        if num_queries > 0:
            total_time = sum(float(q['time']) for q in connection.queries)
            print(f"  Total time: {total_time:.4f}s")
            
            if num_queries > 5:
                print(f"  ⚠️  WARNING: Too many queries! Consider optimization.")
    
    print("\n" + "=" * 60)


def create_health_check_endpoint():
    """Create a health check endpoint for monitoring"""
    print("\n" + "=" * 60)
    print("CREATING HEALTH CHECK ENDPOINT")
    print("=" * 60)
    
    health_check_code = '''
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import time

def health_check(request):
    """
    Health check endpoint for monitoring
    Returns system status and metrics
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'error'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['cache'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Disk space check (basic)
    import shutil
    try:
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100
        health_status['checks']['disk_space'] = {
            'free_percent': round(free_percent, 2),
            'status': 'ok' if free_percent > 10 else 'warning'
        }
        if free_percent < 10:
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['disk_space'] = f'error: {str(e)}'
    
    return JsonResponse(health_status)
'''
    
    # Write to api_views.py
    try:
        with open('core_blood_system/api_views.py', 'r') as f:
            content = f.read()
        
        if 'def health_check' not in content:
            with open('core_blood_system/api_views.py', 'a') as f:
                f.write('\n\n' + health_check_code)
            print("✅ Health check endpoint added to api_views.py")
            print("   Add this to urls.py: path('health/', health_check, name='health_check')")
        else:
            print("ℹ️  Health check endpoint already exists")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print("=" * 60)


def optimize_settings():
    """Suggest settings optimizations"""
    print("\n" + "=" * 60)
    print("RECOMMENDED SETTINGS OPTIMIZATIONS")
    print("=" * 60)
    
    recommendations = """
Add these to your settings.py for better performance:

# Database Connection Pooling
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Caching Configuration (if Redis is available)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'blood_mgmt',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Query Optimization
DEBUG = False  # In production
CONN_MAX_AGE = 600

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/django_warnings.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
"""
    
    print(recommendations)
    print("=" * 60)


if __name__ == '__main__':
    print("\n🚀 BLOOD MANAGEMENT SYSTEM - QUICK IMPROVEMENTS")
    print("=" * 60)
    
    try:
        # 1. Add database indexes
        add_database_indexes()
        
        # 2. Analyze queries
        analyze_slow_queries()
        
        # 3. Create health check
        create_health_check_endpoint()
        
        # 4. Show optimization recommendations
        optimize_settings()
        
        print("\n" + "=" * 60)
        print("✅ ALL QUICK IMPROVEMENTS COMPLETED!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test the application to ensure everything works")
        print("2. Monitor query performance")
        print("3. Review SYSTEM_IMPROVEMENTS_2026.md for more enhancements")
        print("4. Commit and deploy changes")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
