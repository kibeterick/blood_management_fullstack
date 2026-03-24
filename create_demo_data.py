#!/usr/bin/env python
"""
Create Demo Data for Presentation
Populates the system with realistic sample data
"""

import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import (
    CustomUser, Donor, BloodRequest, BloodDonation, 
    BloodInventory, Patient
)

def create_demo_data():
    print("=" * 60)
    print("CREATING DEMO DATA FOR PRESENTATION")
    print("=" * 60)
    
    # Sample data
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    first_names = ['John', 'Mary', 'James', 'Patricia', 'Robert', 'Jennifer', 
                   'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Susan',
                   'Richard', 'Jessica', 'Joseph', 'Sarah', 'Thomas', 'Karen']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                  'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez']
    
    # 1. Create Blood Inventory
    print("\n1. Creating Blood Inventory...")
    for bt in blood_types:
        units = random.randint(5, 30)
        inventory, created = BloodInventory.objects.get_or_create(
            blood_type=bt,
            defaults={
                'units_available': units,
                'low_stock_threshold': 10
            }
        )
        if created:
            print(f"   ✓ Created inventory for {bt}: {units} units")
        else:
            print(f"   - Inventory for {bt} already exists: {inventory.units_available} units")
    
    # 2. Create Sample Users (Donors)
    print("\n2. Creating Sample Donors...")
    donors_created = 0
    for i in range(15):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name.lower()}{last_name.lower()}{i}"
        email = f"{username}@example.com"
        blood_type = random.choice(blood_types)
        
        # Create user
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'blood_type': blood_type,
                'phone_number': f'+254{random.randint(700000000, 799999999)}',
                'role': 'user'
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            
            # Create donor profile
            Donor.objects.create(
                user=user,
                blood_type=blood_type,
                date_of_birth=datetime.now().date() - timedelta(days=random.randint(7300, 18250)),
                address=f"{random.randint(1, 999)} Main Street, Nairobi",
                is_available=random.choice([True, True, True, False])  # 75% available
            )
            donors_created += 1
            print(f"   ✓ Created donor: {first_name} {last_name} ({blood_type})")
    
    print(f"   Total donors created: {donors_created}")
    
    # 3. Create Sample Patients
    print("\n3. Creating Sample Patients...")
    patients_created = 0
    for i in range(8):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        blood_type = random.choice(blood_types)
        
        patient, created = Patient.objects.get_or_create(
            name=f"{first_name} {last_name}",
            defaults={
                'blood_type': blood_type,
                'phone_number': f'+254{random.randint(700000000, 799999999)}',
                'address': f"{random.randint(1, 999)} Hospital Road, Nairobi",
                'date_of_birth': datetime.now().date() - timedelta(days=random.randint(7300, 25550))
            }
        )
        
        if created:
            patients_created += 1
            print(f"   ✓ Created patient: {first_name} {last_name} ({blood_type})")
    
    print(f"   Total patients created: {patients_created}")
    
    # 4. Create Blood Requests
    print("\n4. Creating Blood Requests...")
    patients = list(Patient.objects.all())
    users = list(CustomUser.objects.filter(role='user'))
    
    if patients and users:
        statuses = ['pending', 'approved', 'fulfilled', 'rejected']
        urgencies = ['low', 'medium', 'high', 'critical']
        purposes = ['surgery', 'emergency', 'treatment', 'transfusion']
        
        requests_created = 0
        for i in range(10):
            patient = random.choice(patients)
            requester = random.choice(users)
            
            request, created = BloodRequest.objects.get_or_create(
                patient=patient,
                blood_type=patient.blood_type,
                defaults={
                    'requester': requester,
                    'units_needed': random.randint(1, 5),
                    'urgency': random.choice(urgencies),
                    'purpose': random.choice(purposes),
                    'status': random.choice(statuses),
                    'hospital_name': random.choice(['Kenyatta Hospital', 'Nairobi Hospital', 'Aga Khan Hospital']),
                    'doctor_name': f"Dr. {random.choice(first_names)} {random.choice(last_names)}",
                    'notes': 'Sample blood request for demonstration'
                }
            )
            
            if created:
                requests_created += 1
                print(f"   ✓ Created request: {patient.name} needs {request.units_needed} units of {request.blood_type}")
        
        print(f"   Total requests created: {requests_created}")
    
    # 5. Create Blood Donations
    print("\n5. Creating Blood Donations...")
    donors = list(Donor.objects.all())
    
    if donors:
        donations_created = 0
        for i in range(8):
            donor = random.choice(donors)
            
            donation, created = BloodDonation.objects.get_or_create(
                donor=donor,
                defaults={
                    'blood_type': donor.blood_type,
                    'units_donated': 1,
                    'donation_date': datetime.now().date() - timedelta(days=random.randint(1, 90)),
                    'status': random.choice(['pending', 'approved', 'approved', 'approved']),  # 75% approved
                    'notes': 'Sample donation for demonstration'
                }
            )
            
            if created:
                donations_created += 1
                print(f"   ✓ Created donation: {donor.user.get_full_name()} donated {donor.blood_type}")
        
        print(f"   Total donations created: {donations_created}")
    
    print("\n" + "=" * 60)
    print("✅ DEMO DATA CREATION COMPLETE!")
    print("=" * 60)
    print("\nYour system now has:")
    print(f"- {CustomUser.objects.count()} users")
    print(f"- {Donor.objects.count()} donors")
    print(f"- {Patient.objects.count()} patients")
    print(f"- {BloodRequest.objects.count()} blood requests")
    print(f"- {BloodDonation.objects.count()} donations")
    print(f"- {BloodInventory.objects.count()} inventory items")
    print("\nYour system is ready for presentation! 🎉")
    print("=" * 60)

if __name__ == '__main__':
    create_demo_data()
