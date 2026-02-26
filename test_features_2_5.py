"""
Test script to verify Features 2-5 are properly implemented
Run this before deploying to catch any issues
"""
import os
import sys

def test_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {filepath}")
        return True
    else:
        print(f"✗ MISSING: {filepath}")
        return False

def test_import(module_path):
    """Test if a Python module can be imported"""
    try:
        __import__(module_path)
        print(f"✓ Import: {module_path}")
        return True
    except Exception as e:
        print(f"✗ Import failed: {module_path} - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Testing Features 2-5 Implementation")
    print("=" * 60)
    
    all_passed = True
    
    # Test view files
    print("\n1. Testing View Files...")
    view_files = [
        'core_blood_system/views_notifications.py',
        'core_blood_system/views_matching.py',
        'core_blood_system/views_analytics.py',
        'core_blood_system/views_qrcode.py',
    ]
    for f in view_files:
        if not test_file_exists(f):
            all_passed = False
    
    # Test template files
    print("\n2. Testing Template Files...")
    template_files = [
        'core_blood_system/templates/notifications/notification_center.html',
        'core_blood_system/templates/matching/match_results.html',
        'core_blood_system/templates/matching/my_matches.html',
        'core_blood_system/templates/matching/admin_matching_dashboard.html',
        'core_blood_system/templates/analytics/dashboard.html',
        'core_blood_system/templates/qr_codes/scanner.html',
        'core_blood_system/templates/qr_codes/my_qr_codes.html',
    ]
    for f in template_files:
        if not test_file_exists(f):
            all_passed = False
    
    # Test imports
    print("\n3. Testing Python Imports...")
    modules = [
        'core_blood_system.views_notifications',
        'core_blood_system.views_matching',
        'core_blood_system.views_analytics',
        'core_blood_system.views_qrcode',
        'core_blood_system.enhancements',
    ]
    for m in modules:
        if not test_import(m):
            all_passed = False
    
    # Test models
    print("\n4. Testing Models...")
    try:
        from core_blood_system.models import (
            DonationAppointment, Notification, MatchedDonor, QRCode
        )
        print("✓ All enhancement models imported successfully")
    except Exception as e:
        print(f"✗ Model import failed: {str(e)}")
        all_passed = False
    
    # Test URLs
    print("\n5. Testing URLs Configuration...")
    try:
        from core_blood_system import urls
        url_patterns = [str(p.pattern) for p in urls.urlpatterns]
        
        required_urls = [
            'notifications/',
            'matching/',
            'analytics/',
            'qr/',
        ]
        
        for url in required_urls:
            found = any(url in pattern for pattern in url_patterns)
            if found:
                print(f"✓ URL pattern found: {url}")
            else:
                print(f"✗ URL pattern missing: {url}")
                all_passed = False
                
    except Exception as e:
        print(f"✗ URL test failed: {str(e)}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED! Ready to deploy.")
    else:
        print("❌ SOME TESTS FAILED! Please fix issues before deploying.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
