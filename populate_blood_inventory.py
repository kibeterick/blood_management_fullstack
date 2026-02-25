#!/usr/bin/env python
"""
Script to populate blood inventory with initial data for all 8 blood types
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import BloodInventory

def populate_inventory():
    """Create or update blood inventory for all blood types"""
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    # Initial units for each blood type (you can adjust these)
    initial_units = {
        'A+': 15,
        'A-': 8,
        'B+': 12,
        'B-': 6,
        'AB+': 10,
        'AB-': 5,
        'O+': 20,
        'O-': 7,
    }
    
    print("Populating blood inventory...")
    print("-" * 50)
    
    for blood_type in blood_types:
        units = initial_units.get(blood_type, 10)
        inventory, created = BloodInventory.objects.get_or_create(
            blood_type=blood_type,
            defaults={'units_available': units, 'minimum_threshold': 5}
        )
        
        if created:
            print(f"✓ Created {blood_type}: {units} units")
        else:
            # Update existing inventory
            inventory.units_available = units
            inventory.save()
            print(f"✓ Updated {blood_type}: {units} units")
    
    print("-" * 50)
    print("Blood inventory populated successfully!")
    print("\nCurrent Inventory:")
    for item in BloodInventory.objects.all().order_by('blood_type'):
        status = "LOW STOCK" if item.is_low_stock() else "Adequate"
        print(f"  {item.blood_type}: {item.units_available} units [{status}]")

if __name__ == '__main__':
    populate_inventory()
