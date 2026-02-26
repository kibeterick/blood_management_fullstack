#!/usr/bin/env python
"""
Check if certificate dependencies are installed
"""
import sys

print("=" * 60)
print("CHECKING CERTIFICATE DEPENDENCIES")
print("=" * 60)

# Check reportlab
try:
    import reportlab
    print(f"\n✓ reportlab is installed (version {reportlab.Version})")
    
    # Check specific modules
    try:
        from reportlab.lib.pagesizes import letter, A4
        print("  ✓ reportlab.lib.pagesizes")
    except ImportError as e:
        print(f"  ✗ reportlab.lib.pagesizes: {e}")
    
    try:
        from reportlab.pdfgen import canvas
        print("  ✓ reportlab.pdfgen.canvas")
    except ImportError as e:
        print(f"  ✗ reportlab.pdfgen.canvas: {e}")
    
    try:
        from reportlab.lib import colors
        print("  ✓ reportlab.lib.colors")
    except ImportError as e:
        print(f"  ✗ reportlab.lib.colors: {e}")
    
    print("\n✓✓✓ All certificate dependencies are installed!")
    print("Certificate feature is ready to use.")
    
except ImportError:
    print("\n✗ reportlab is NOT installed")
    print("\nTo install reportlab, run:")
    print("  pip install reportlab")
    sys.exit(1)

print("\n" + "=" * 60)
print("TESTING CERTIFICATE GENERATION")
print("=" * 60)

# Test certificate generation
try:
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    from core_blood_system.models import BloodDonation
    
    # Check if there are any donations
    donation_count = BloodDonation.objects.count()
    print(f"\nDonations in database: {donation_count}")
    
    if donation_count > 0:
        print("\n✓ You can generate certificates for these donations")
        print("  Go to: https://kibeterick.pythonanywhere.com/my-donations/")
        
        # Show first few donations
        donations = BloodDonation.objects.all()[:5]
        print("\nRecent donations:")
        for d in donations:
            print(f"  - {d.donor.full_name} | {d.blood_type} | {d.donation_date}")
    else:
        print("\n⚠ No donations in database yet")
        print("  You need to approve donation requests first")
        print("  Go to: Manage → Donation Requests")
    
except Exception as e:
    print(f"\n⚠ Could not check donations: {e}")

print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)
