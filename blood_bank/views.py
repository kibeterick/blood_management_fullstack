from django.shortcuts import render
from django.http import JsonResponse
from .models import BloodDonor, BloodBank, BloodRecipient, BloodDonation, BloodInventory

def blood_donors_list(request):
    donors = BloodDonor.objects.all()
    donor_list = []
    for donor in donors:
        donor_list.append({
            "id": donor.id,
            "name": donor.name,
            "age": donor.age,
            "gender": donor.gender,
            "blood_type": donor.blood_type,
            "contact_number": donor.contact_number,
            "email": donor.email,
            "is_available": donor.is_available
        })
    return JsonResponse({"message": "Blood donors list", "data": donor_list})

def blood_banks_list(request):
    banks = BloodBank.objects.all()
    bank_list = []
    for bank in banks:
        bank_list.append({
            "id": bank.id,
            "name": bank.name,
            "address": bank.address,
            "contact_number": bank.contact_number,
            "email": bank.email,
            "capacity": bank.capacity,
            "current_stock": bank.current_stock
        })
    return JsonResponse({"message": "Blood banks list", "data": bank_list})

def blood_recipients_list(request):
    recipients = BloodRecipient.objects.all()
    recipient_list = []
    for recipient in recipients:
        recipient_list.append({
            "id": recipient.id,
            "name": recipient.name,
            "age": recipient.age,
            "blood_type": recipient.blood_type,
            "contact_number": recipient.contact_number,
            "email": recipient.email,
            "hospital_name": recipient.hospital_name,
            "urgency_level": recipient.urgency_level,
            "blood_units_required": recipient.blood_units_required,
            "date_needed": recipient.date_needed,
            "is_fulfilled": recipient.is_fulfilled
        })
    return JsonResponse({"message": "Blood recipients list", "data": recipient_list})

def blood_donations_list(request):
    donations = BloodDonation.objects.all()
    donation_list = []
    for donation in donations:
        donation_list.append({
            "id": donation.id,
            "donor_name": donation.donor.name,
            "recipient_name": donation.recipient.name if donation.recipient else None,
            "blood_bank_name": donation.blood_bank.name,
            "donation_date": donation.donation_date,
            "blood_units": donation.blood_units,
            "status": donation.status
        })
    return JsonResponse({"message": "Blood donations list", "data": donation_list})

def blood_inventory_list(request):
    inventory = BloodInventory.objects.all()
    inventory_list = []
    for item in inventory:
        inventory_list.append({
            "id": item.id,
            "blood_bank_name": item.blood_bank.name,
            "blood_type": item.blood_type,
            "units_available": item.units_available,
            "last_updated": item.last_updated
        })
    return JsonResponse({"message": "Blood inventory list", "data": inventory_list})