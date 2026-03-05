"""
Create BloodUnit Table in PythonAnywhere Database
This script creates the missing core_blood_system_bloodunit table
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def create_bloodunit_table():
    """Create the BloodUnit table"""
    print("Creating BloodUnit table...")
    
    with connection.cursor() as cursor:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='core_blood_system_bloodunit'
        """)
        
        if cursor.fetchone():
            print("✓ BloodUnit table already exists")
            return
        
        # Create the table
        cursor.execute("""
            CREATE TABLE core_blood_system_bloodunit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blood_type VARCHAR(3) NOT NULL,
                donation_id INTEGER NULL,
                donation_date DATE NOT NULL,
                expiration_date DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'available',
                unit_number VARCHAR(50) NOT NULL UNIQUE,
                volume_ml INTEGER NOT NULL DEFAULT 450,
                storage_location VARCHAR(100) NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (donation_id) REFERENCES core_blood_system_blooddonation(id) ON DELETE SET NULL
            )
        """)
        print("✓ Created BloodUnit table")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX idx_bloodunit_type_status 
            ON core_blood_system_bloodunit(blood_type, status)
        """)
        print("✓ Created index on blood_type and status")
        
        cursor.execute("""
            CREATE INDEX idx_bloodunit_expiration 
            ON core_blood_system_bloodunit(expiration_date)
        """)
        print("✓ Created index on expiration_date")
    
    print("✅ BloodUnit table created successfully!")

if __name__ == '__main__':
    try:
        create_bloodunit_table()
        print("\n🎉 Database setup complete!")
        print("\nYou can now access:")
        print("  - Inventory Dashboard: /inventory/")
        print("  - Add Blood Units: /inventory/add-unit/")
        print("  - Expiration Tracking: /inventory/expiration/")
        print("  - Configure Thresholds: /inventory/configure-thresholds/")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
