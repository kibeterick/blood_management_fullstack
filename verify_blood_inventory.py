#!/usr/bin/env python
"""
Script to verify blood inventory is properly set up and display current status
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import BloodInventory

def verify_inventory():
    """Verify blood inventory setup and display status"""
    print("=" * 60)
    print("BLOOD INVENTORY VERIFICATION")
    print("=" * 60)
    
    # Check if inventory exists
    inventory_count = BloodInventory.objects.count()
    
    if inventory_count == 0:
        print("\n❌ ERROR: No blood inventory found!")
        print("\nTo fix this, run:")
        print("  python populate_blood_inventory.py")
        return
    
    print(f"\n✓ Found {inventory_count} blood type(s) in inventory")
    print("\n" + "-" * 60)
    print(f"{'Blood Type':<12} {'Units':<10} {'Status':<15} {'Fill %':<10}")
    print("-" * 60)
    
    total_units = 0
    low_stock_count = 0
    
    for item in BloodInventory.objects.all().order_by('blood_type'):
        status = "⚠️  LOW STOCK" if item.is_low_stock() else "✓ Adequate"
        fill_percentage = min((item.units_available / 25) * 100, 100)
        
        # Visual bar representation
        bar_length = int(fill_percentage / 10)
        bar = "█" * bar_length + "░" * (10 - bar_length)
        
        print(f"{item.blood_type:<12} {item.units_available:<10} {status:<15} {bar} {fill_percentage:.0f}%")
        
        total_units += item.units_available
        if item.is_low_stock():
            low_stock_count += 1
    
    print("-" * 60)
    print(f"\nTOTAL UNITS: {total_units}")
    print(f"LOW STOCK ITEMS: {low_stock_count}")
    
    if low_stock_count > 0:
        print(f"\n⚠️  WARNING: {low_stock_count} blood type(s) are running low!")
        print("Consider organizing donation drives for:")
        for item in BloodInventory.objects.filter(units_available__lt=5):
            print(f"  - {item.blood_type} (only {item.units_available} units)")
    else:
        print("\n✓ All blood types have adequate stock!")
    
    print("\n" + "=" * 60)
    print("DASHBOARD STATUS")
    print("=" * 60)
    
    # Check if admin dashboard will display correctly
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    admin_count = User.objects.filter(role='admin').count()
    print(f"\n✓ Admin users: {admin_count}")
    
    if admin_count > 0:
        print("\nTo view the blood bag visualization:")
        print("1. Run: python manage.py runserver")
        print("2. Go to: http://127.0.0.1:8000/login/")
        print("3. Login as admin")
        print("4. View the animated blood bags on the dashboard!")
    else:
        print("\n❌ No admin users found!")
        print("Create an admin user first:")
        print("  python manage.py createsuperuser")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    verify_inventory()
