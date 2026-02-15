from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Donor, BloodRequest, BloodDonation, BloodInventory


# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'blood_type', 'is_staff']
    list_filter = ['role', 'blood_type', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address', 'blood_type', 'date_of_birth')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'blood_type')}),
    )


# Donor Admin
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'blood_type', 'email', 'phone_number', 
                    'is_available', 'last_donation_date', 'created_at']
    list_filter = ['blood_type', 'is_available', 'city', 'state']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth')
        }),
        ('Blood Information', {
            'fields': ('blood_type', 'last_donation_date', 'is_available')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state')
        }),
    )


# Blood Request Admin
@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_type', 'purpose', 'urgency', 'units_needed', 
                    'status', 'required_date', 'created_at']
    list_filter = ['blood_type', 'purpose', 'urgency', 'status', 'created_at']
    search_fields = ['patient_name', 'hospital_name', 'requester__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('requester', 'patient_name')
        }),
        ('Blood Requirements', {
            'fields': ('blood_type', 'units_needed', 'purpose', 'purpose_details', 'urgency')
        }),
        ('Hospital Information', {
            'fields': ('hospital_name', 'hospital_address', 'contact_number')
        }),
        ('Request Details', {
            'fields': ('required_date', 'status', 'notes', 'fulfilled_date')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['created_at', 'updated_at']
        return self.readonly_fields


# Blood Donation Admin
@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_type', 'units_donated', 'donation_date', 'hospital_name', 'created_at']
    list_filter = ['blood_type', 'donation_date']
    search_fields = ['donor__first_name', 'donor__last_name', 'hospital_name']
    date_hierarchy = 'donation_date'
    ordering = ['-donation_date']
    
    fieldsets = (
        ('Donation Information', {
            'fields': ('donor', 'blood_request', 'donation_date', 'blood_type', 'units_donated')
        }),
        ('Hospital Information', {
            'fields': ('hospital_name', 'notes')
        }),
    )
    
    readonly_fields = ['created_at']


# Blood Inventory Admin
@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['blood_type', 'units_available', 'minimum_threshold', 'is_low_stock', 'last_updated']
    list_filter = ['blood_type']
    ordering = ['blood_type']
    
    fieldsets = (
        ('Inventory Details', {
            'fields': ('blood_type', 'units_available', 'minimum_threshold')
        }),
    )
    
    readonly_fields = ['last_updated']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'