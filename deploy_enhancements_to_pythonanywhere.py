"""
Deploy Blood Management Enhancements to PythonAnywhere
This script adds the new database fields and enables advanced features
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def add_inventory_fields():
    """Add new fields to BloodInventory table"""
    print("Adding new fields to BloodInventory...")
    
    with connection.cursor() as cursor:
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(core_blood_system_bloodinventory)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add critical_threshold if it doesn't exist
        if 'critical_threshold' not in columns:
            cursor.execute("""
                ALTER TABLE core_blood_system_bloodinventory 
                ADD COLUMN critical_threshold INTEGER DEFAULT 2
            """)
            print("✓ Added critical_threshold field")
        
        # Add optimal_level if it doesn't exist
        if 'optimal_level' not in columns:
            cursor.execute("""
                ALTER TABLE core_blood_system_bloodinventory 
                ADD COLUMN optimal_level INTEGER DEFAULT 20
            """)
            print("✓ Added optimal_level field")
        
        # Add alert_sent_at if it doesn't exist
        if 'alert_sent_at' not in columns:
            cursor.execute("""
                ALTER TABLE core_blood_system_bloodinventory 
                ADD COLUMN alert_sent_at DATETIME NULL
            """)
            print("✓ Added alert_sent_at field")
    
    print("✅ Database fields added successfully!")

if __name__ == '__main__':
    try:
        add_inventory_fields()
        print("\n🎉 Enhancement deployment complete!")
        print("\nNew features enabled:")
        print("  - Advanced Inventory Management")
        print("  - Inventory Thresholds Configuration")
        print("  - Expiration Tracking")
        print("  - Low Stock Alerts")
        print("\nAccess at: /inventory/")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
