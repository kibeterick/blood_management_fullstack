#!/usr/bin/env python
"""
Migration script to add donor eligibility tracking fields to existing database
Run this on PythonAnywhere after pulling the latest code
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/kibeterick/blood_management_fullstack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

def add_eligibility_fields():
    """Add eligibility tracking fields to Donor table"""
    print("🔧 Adding donor eligibility tracking fields...")
    
    with connection.cursor() as cursor:
        try:
            # Check if fields already exist
            cursor.execute("PRAGMA table_info(core_blood_system_donor)")
            columns = [row[1] for row in cursor.fetchall()]
            
            fields_to_add = []
            
            if 'next_eligible_date' not in columns:
                fields_to_add.append(
                    "ALTER TABLE core_blood_system_donor ADD COLUMN next_eligible_date DATE NULL"
                )
            
            if 'is_eligible_override' not in columns:
                fields_to_add.append(
                    "ALTER TABLE core_blood_system_donor ADD COLUMN is_eligible_override BOOLEAN DEFAULT 0 NOT NULL"
                )
            
            if 'eligibility_notes' not in columns:
                fields_to_add.append(
                    "ALTER TABLE core_blood_system_donor ADD COLUMN eligibility_notes TEXT NULL"
                )
            
            # Execute alterations
            for sql in fields_to_add:
                print(f"  Executing: {sql}")
                cursor.execute(sql)
            
            if fields_to_add:
                print(f"✅ Added {len(fields_to_add)} new field(s) to Donor table")
            else:
                print("✅ All eligibility fields already exist")
            
            # Calculate next_eligible_date for existing donors
            print("\n🔄 Calculating eligibility dates for existing donors...")
            cursor.execute("""
                UPDATE core_blood_system_donor 
                SET next_eligible_date = DATE(last_donation_date, '+56 days')
                WHERE last_donation_date IS NOT NULL 
                AND is_eligible_override = 0
            """)
            updated = cursor.rowcount
            print(f"✅ Updated {updated} donor(s) with calculated eligibility dates")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

def verify_fields():
    """Verify that all fields were added successfully"""
    print("\n🔍 Verifying donor eligibility fields...")
    
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(core_blood_system_donor)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_fields = {
            'next_eligible_date': 'DATE',
            'is_eligible_override': 'BOOLEAN',
            'eligibility_notes': 'TEXT'
        }
        
        all_present = True
        for field, expected_type in required_fields.items():
            if field in columns:
                print(f"  ✅ {field}: {columns[field]}")
            else:
                print(f"  ❌ {field}: MISSING")
                all_present = False
        
        return all_present

def show_donor_stats():
    """Show donor eligibility statistics"""
    from core_blood_system.models import Donor
    
    print("\n📊 Donor Eligibility Statistics:")
    print("=" * 50)
    
    total_donors = Donor.objects.count()
    eligible_donors = sum(1 for d in Donor.objects.all() if d.is_eligible())
    ineligible_donors = total_donors - eligible_donors
    override_donors = Donor.objects.filter(is_eligible_override=True).count()
    
    print(f"  Total Donors: {total_donors}")
    print(f"  ✅ Eligible to Donate: {eligible_donors}")
    print(f"  ❌ Not Eligible: {ineligible_donors}")
    print(f"  🔓 Admin Override: {override_donors}")
    
    # Show donors waiting to be eligible
    if ineligible_donors > 0:
        print("\n⏳ Donors Waiting to Be Eligible:")
        for donor in Donor.objects.all():
            if not donor.is_eligible() and not donor.is_eligible_override:
                days = donor.days_until_eligible()
                next_date = donor.calculate_next_eligible_date()
                print(f"  • {donor.first_name} {donor.last_name} ({donor.blood_type}): {days} days (Next: {next_date})")

if __name__ == '__main__':
    print("=" * 60)
    print("🩸 DONOR ELIGIBILITY TRACKING - DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    try:
        # Add fields
        add_eligibility_fields()
        
        # Verify
        if verify_fields():
            print("\n✅ All eligibility fields verified successfully!")
        else:
            print("\n❌ Some fields are missing. Please check the errors above.")
            sys.exit(1)
        
        # Show stats
        show_donor_stats()
        
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETE!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("  1. Reload your web app on PythonAnywhere")
        print("  2. Visit the donor list page to see eligibility badges")
        print("  3. Admins can override eligibility in the admin panel")
        print()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
