import os, sys, django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from core_blood_system.models import Donor, Donation, Recipient
from datetime import date, timedelta

print("Populating DB...")
d1 = Donor.objects.create(first_name="John", last_name="Doe", email="john@mail.com", phone="0712345678", blood_type="O+", gender="Male", date_of_birth="1990-01-01")
d2 = Donor.objects.create(first_name="Alice", last_name="Smith", email="alice@mail.com", phone="0723456789", blood_type="A-", gender="Female", date_of_birth="1995-05-15")
d3 = Donor.objects.create(first_name="Bob", last_name="Muli", email="bob@mail.com", phone="0734567890", blood_type="AB+", gender="Male", date_of_birth="1988-11-30")
Donation.objects.create(donor=d1, donation_date=date.today(), blood_type="O+", status="Approved", expiry_date=date.today() + timedelta(days=30))
Donation.objects.create(donor=d2, donation_date=date.today(), blood_type="A-", status="Approved", expiry_date=date.today() + timedelta(days=5))
Donation.objects.create(donor=d3, donation_date=date.today(), blood_type="AB+", status="Approved", expiry_date=date.today() + timedelta(days=60))
Recipient.objects.create(first_name="Sarah", last_name="Kemei", blood_type="O+", hospital_name="Kenyatta Hospital", phone="0711222333", quantity_required_ml=450)
print("SUCCESS: Database populated!")