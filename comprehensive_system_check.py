#!/usr/bin/env python
"""
Comprehensive System Check for Blood Management System
Checks for errors, missing data, and potential issues before presentation
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import (
    CustomUser, Donor, BloodRequest, BloodDonation, 
    BloodInventory, Patient
)

def check_system():
    print("=" * 60)
    print("BLOOD MANAGEMENT SYSTEM - COMPREHENSIVE CHECK")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # 1. Check Users
    print("\n1. CHECKING USERS...")
    total_users = CustomUser.objects.count()
    admin_users = CustomUser.objects.filter(role='admin').count()
    regular_users = CustomUser.objects.filter(role='user').count()
    
    print(f"   ✓ Total Users: {total_users}")
    print(f"   ✓ Admin Users: {admin_users}")
    print(f"   ✓ Regular Users: {regular_users}")
    
    if admin_users == 0:
        issues.append("No admin users found!")
    
    # 2. Check Donors
    print("\n2. CHECKING DONORS...")
    total_donors = Donor.objects.count()
    print(f"   ✓ Total Donors: {total_donors}")
    
    if total_donors == 0:
        warnings.append("No donors in system - consider adding sample data")
    
    # Check blood type distribution
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    for bt in blood_types:
        count = Donor.objects.filter(blood_type=bt).count()
        print(f"   - {bt}: {count} donors")
    
    # 3. Check Blood Requests
    print("\n3. CHECKING BLOOD REQUESTS...")
    total_requests = BloodRequest.objects.count()
    pending = BloodRequest.objects.filter(status='pending').count()
    approved = BloodRequest.objects.filter(status='approved').count()
    fulfilled = BloodRequest.objects.filter(status='fulfilled').count()
    
    print(f"   ✓ Total Requests: {total_requests}")
    print(f"   - Pending: {pending}")
    print(f"   - Approved: {approved}")
    print(f"   - Fulfilled: {fulfilled}")
    
    if total_requests == 0:
        warnings.append("No blood requests - dashboard will look empty")
    
    # 4. Check Blood Donations
    print("\n4. CHECKING BLOOD DONATIONS...")
    total_donations = BloodDonation.objects.count()
    print(f"   ✓ Total Donations: {total_donations}")
    
    if total_donations == 0:
        warnings.append("No donations recorded")
    
    # 5. Check Blood Inventory
    print("\n5. CHECKING BLOOD INVENTORY...")
    inventory_items = BloodInventory.objects.count()
    print(f"   ✓ Inventory Items: {inventory_items}")
    
    if inventory_items == 0:
        issues.append("Blood inventory is empty! Dashboard will show no data")
        print("   ⚠ Creating default inventory...")
        for bt in blood_types:
            BloodInventory.objects.get_or_create(
                blood_type=bt,
                defaults={'units_available': 10, 'low_stock_threshold': 5}
            )
        print("   ✓ Default inventory created")
    else:
        for item in BloodInventory.objects.all():
            status = "LOW STOCK!" if item.is_low_stock else "OK"
            print(f"   - {item.blood_type}: {item.units_available} units [{status}]")
    
    # 6. Check Patients
    print("\n6. CHECKING PATIENTS...")
    total_patients = Patient.objects.count()
    print(f"   ✓ Total Patients: {total_patients}")
    
    if total_patients == 0:
        warnings.append("No patients registered")
    
    # 7. Check for orphaned data
    print("\n7. CHECKING DATA INTEGRITY...")
    
    # Check for requests without patients
    requests_without_patient = BloodRequest.objects.filter(patient__isnull=True).count()
    if requests_without_patient > 0:
        warnings.append(f"{requests_without_patient} blood requests without patient")
    
    # Check for donations without donors
    donations_without_donor = BloodDonation.objects.filter(donor__isnull=True).count()
    if donations_without_donor > 0:
        warnings.append(f"{donations_without_donor} donations without donor")
    
    print("   ✓ Data integrity check complete")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if not issues and not warnings:
        print("✅ ALL CHECKS PASSED! System is ready for presentation!")
    else:
        if issues:
            print(f"\n❌ CRITICAL ISSUES ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        if warnings:
            print(f"\n⚠ WARNINGS ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS FOR PRESENTATION:")
    print("=" * 60)
    print("1. Add sample donors (at least 10-15)")
    print("2. Create 3-5 blood requests with different statuses")
    print("3. Record 2-3 donations")
    print("4. Ensure blood inventory has varied stock levels")
    print("5. Test all major features before presenting")
    print("=" * 60)

if __name__ == '__main__':
    check_system()
