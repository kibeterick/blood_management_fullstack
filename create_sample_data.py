"""
Create Sample Data for Testing Features 2-5
Run this script to populate your database with test data
"""
import os
import django
import sys
from datetime import datetime, timedelta
from random import choice, randint

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_blood_system.models import (
    CustomUser, Donor, BloodRequest, BloodDonation, BloodInventory,
    DonationAppointment, Notification, MatchedDonor
)
from core_blood_system.enhancements import match_donors_to_request, create_notification

def create_sample_users():
    """Create sample users"""
    print("\n📝 Creating sample users...")
    
    users_data = [
        {'username': 'john_donor', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'role': 'user', 'blood_type': 'O+'},
        {'username': 'jane_donor', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'user', 'blood_type': 'A+'},
        {'username': 'mike_donor', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Johnson', 'role': 'user', 'blood_type': 'B+'},
        {'username': 'sarah_donor', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Williams', 'role': 'user', 'blood_type': 'AB+'},
        {'username': 'david_donor', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Brown', 'role': 'user', 'blood_type': 'O-'},
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = CustomUser.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'blood_type': user_data['blood_type'],
                'phone_number': f'+254{randint(700000000, 799999999)}',
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✓ Created user: {user.username}")
        else:
            print(f"  ℹ User already exists: {user.username}")
        created_users.append(user)
    
    return created_users


def create_sample_donors(users):
    """Create sample donors"""
    print("\n🩸 Creating sample donors...")
    
    cities = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
    blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
    
    created_donors = []
    for i, user in enumerate(users):
        donor, created = Donor.objects.get_or_create(
            email=user.email,
            defaults={
                'user': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'gender': choice(['male', 'female']),
                'blood_type': user.blood_type or choice(blood_types),
                'date_of_birth': datetime.now().date() - timedelta(days=randint(7300, 18250)),  # 20-50 years old
                'address': f'{randint(1, 999)} Main Street',
                'city': choice(cities),
                'state': 'Kenya',
                'is_available': True,
                'last_donation_date': datetime.now().date() - timedelta(days=randint(60, 180)) if i % 2 == 0 else None,
            }
        )
        if created:
            print(f"  ✓ Created donor: {donor.first_name} {donor.last_name} ({donor.blood_type})")
        else:
            print(f"  ℹ Donor already exists: {donor.first_name} {donor.last_name}")
        created_donors.append(donor)
    
    return created_donors


def create_sample_blood_requests(users):
    """Create sample blood requests"""
    print("\n📋 Creating sample blood requests...")
    
    blood_types = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']
    purposes = ['surgery', 'emergency', 'accident', 'anemia', 'cancer']
    urgencies = ['low', 'medium', 'high', 'critical']
    hospitals = ['Kenyatta National Hospital', 'Nairobi Hospital', 'Aga Khan Hospital', 'Mater Hospital']
    
    created_requests = []
    for i in range(5):
        request, created = BloodRequest.objects.get_or_create(
            patient_name=f"Patient {i+1}",
            blood_type=choice(blood_types),
            defaults={
                'requester': choice(users),
                'patient_gender': choice(['male', 'female']),
                'patient_age': randint(18, 70),
                'units_needed': randint(1, 4),
                'purpose': choice(purposes),
                'purpose_details': f'Medical emergency requiring {choice(blood_types)} blood',
                'urgency': choice(urgencies),
                'hospital_name': choice(hospitals),
                'hospital_address': f'{randint(1, 999)} Hospital Road, Nairobi',
                'contact_number': f'+254{randint(700000000, 799999999)}',
                'required_date': datetime.now().date() + timedelta(days=randint(1, 7)),
                'status': choice(['pending', 'pending', 'approved']),  # More pending
            }
        )
        if created:
            print(f"  ✓ Created blood request: {request.patient_name} needs {request.blood_type}")
        else:
            print(f"  ℹ Blood request already exists: {request.patient_name}")
        created_requests.append(request)
    
    return created_requests


def create_sample_appointments(donors, users):
    """Create sample appointments"""
    print("\n📅 Creating sample appointments...")
    
    locations = ['Kenyatta National Hospital', 'Nairobi Hospital', 'Aga Khan Hospital']
    time_slots = ['09:00', '10:00', '11:00', '13:00', '14:00', '15:00']
    statuses = ['scheduled', 'confirmed', 'completed']
    
    created_appointments = []
    for i, donor in enumerate(donors[:3]):  # Create appointments for first 3 donors
        appointment, created = DonationAppointment.objects.get_or_create(
            donor=donor,
            appointment_date=datetime.now().date() + timedelta(days=randint(1, 14)),
            defaults={
                'user': donor.user,
                'time_slot': choice(time_slots),
                'location': choice(locations),
                'address': f'{randint(1, 999)} Hospital Road, Nairobi',
                'status': choice(statuses),
                'notes': 'Regular blood donation appointment',
            }
        )
        if created:
            print(f"  ✓ Created appointment: {donor.first_name} on {appointment.appointment_date}")
        else:
            print(f"  ℹ Appointment already exists for {donor.first_name}")
        created_appointments.append(appointment)
    
    return created_appointments


def create_sample_notifications(users):
    """Create sample notifications"""
    print("\n🔔 Creating sample notifications...")
    
    notification_types = ['appointment', 'blood_request', 'donation', 'match', 'system']
    
    notifications_data = [
        {
            'type': 'appointment',
            'title': 'Appointment Reminder',
            'message': 'Your blood donation appointment is tomorrow at 10:00 AM',
            'link': '/appointments/my/',
        },
        {
            'type': 'match',
            'title': 'Blood Request Match',
            'message': 'You match a critical blood request for O+ blood type',
            'link': '/matching/my-matches/',
        },
        {
            'type': 'system',
            'title': 'Welcome to Blood Management System',
            'message': 'Thank you for registering as a blood donor. Your profile is now active.',
            'link': '/dashboard/',
        },
        {
            'type': 'urgent',
            'title': 'Urgent Blood Request',
            'message': 'Critical blood request for AB+ blood type. Immediate donation needed.',
            'link': '/blood-requests/',
        },
    ]
    
    created_notifications = []
    for user in users[:3]:  # Create notifications for first 3 users
        for notif_data in notifications_data[:2]:  # 2 notifications per user
            notification, created = Notification.objects.get_or_create(
                user=user,
                title=notif_data['title'],
                defaults={
                    'notification_type': notif_data['type'],
                    'message': notif_data['message'],
                    'link': notif_data['link'],
                    'is_read': choice([True, False]),
                }
            )
            if created:
                print(f"  ✓ Created notification for {user.username}: {notification.title}")
            else:
                print(f"  ℹ Notification already exists for {user.username}")
            created_notifications.append(notification)
    
    return created_notifications


def create_sample_matches(blood_requests, donors):
    """Create sample donor matches"""
    print("\n💝 Creating sample donor matches...")
    
    created_matches = []
    for request in blood_requests[:2]:  # Match first 2 requests
        print(f"\n  Matching donors for request: {request.patient_name} ({request.blood_type})")
        
        # Find compatible donors
        compatible_donors = [d for d in donors if d.blood_type == request.blood_type]
        
        for donor in compatible_donors[:2]:  # Match with first 2 compatible donors
            match, created = MatchedDonor.objects.get_or_create(
                blood_request=request,
                donor=donor,
                defaults={
                    'match_score': randint(70, 100),
                    'distance_km': randint(5, 50),
                    'status': choice(['matched', 'notified', 'accepted']),
                }
            )
            if created:
                print(f"    ✓ Matched {donor.first_name} {donor.last_name} (Score: {match.match_score})")
            else:
                print(f"    ℹ Match already exists for {donor.first_name}")
            created_matches.append(match)
    
    return created_matches


def create_sample_donations(donors):
    """Create sample blood donations"""
    print("\n🩸 Creating sample donations...")
    
    hospitals = ['Kenyatta National Hospital', 'Nairobi Hospital', 'Aga Khan Hospital']
    
    created_donations = []
    for i, donor in enumerate(donors[:3]):  # Create donations for first 3 donors
        donation, created = BloodDonation.objects.get_or_create(
            donor=donor,
            donation_date=datetime.now().date() - timedelta(days=randint(30, 90)),
            defaults={
                'units_donated': randint(1, 2),
                'blood_type': donor.blood_type,
                'hospital_name': choice(hospitals),
                'status': 'approved',
                'notes': 'Regular blood donation',
            }
        )
        if created:
            print(f"  ✓ Created donation: {donor.first_name} donated {donation.units_donated} unit(s)")
        else:
            print(f"  ℹ Donation already exists for {donor.first_name}")
        created_donations.append(donation)
    
    return created_donations


def main():
    """Main function to create all sample data"""
    print("=" * 60)
    print("🚀 CREATING SAMPLE DATA FOR TESTING")
    print("=" * 60)
    
    try:
        # Create sample data
        users = create_sample_users()
        donors = create_sample_donors(users)
        blood_requests = create_sample_blood_requests(users)
        appointments = create_sample_appointments(donors, users)
        notifications = create_sample_notifications(users)
        matches = create_sample_matches(blood_requests, donors)
        donations = create_sample_donations(donors)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  • Users: {len(users)}")
        print(f"  • Donors: {len(donors)}")
        print(f"  • Blood Requests: {len(blood_requests)}")
        print(f"  • Appointments: {len(appointments)}")
        print(f"  • Notifications: {len(notifications)}")
        print(f"  • Matches: {len(matches)}")
        print(f"  • Donations: {len(donations)}")
        
        print("\n🔐 Test User Credentials:")
        print("  Username: john_donor")
        print("  Password: password123")
        print("\n  (All test users have password: password123)")
        
        print("\n🎯 Next Steps:")
        print("  1. Login to https://kibeterick.pythonanywhere.com")
        print("  2. Check notification bell (should show count)")
        print("  3. Visit Analytics dashboard")
        print("  4. Check Matching dashboard")
        print("  5. View appointments")
        print("  6. Test QR code scanner")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
