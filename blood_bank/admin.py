from django.contrib import admin
from .models import BloodDonor, BloodBank, BloodRecipient, BloodDonation, BloodInventory


@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_type', 'contact_number', 'last_donation_date', 'is_available')
    search_fields = ('name', 'email')
    list_filter = ('blood_type', 'is_available')


@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'operating_hours', 'capacity', 'current_stock')
    search_fields = ('name', 'email')
    list_filter = ('is_available', 'blood_type')


@admin.register(BloodRecipient)
class BloodRecipientAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_type', 'hospital_name', 'urgency_level', 'date_needed', 'is_fulfilled')
    search_fields = ('name', 'email', 'hospital_name')
    list_filter = ('status', 'blood_type')


@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'recipient', 'blood_bank', 'donation_date', 'blood_units', 'status')
    search_fields = ('donor__name', 'recipient__name', 'blood_bank__name')
    list_filter = ('status', 'blood_type')


@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ('blood_bank', 'blood_type', 'units_available', 'last_updated')
    search_fields = ('blood_bank__name', 'blood_type')
    list_filter = ('blood_type', 'blood_bank')