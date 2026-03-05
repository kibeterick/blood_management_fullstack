from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    CustomUser, Donor, BloodRequest, BloodDonation, BloodUnit, BloodInventory,
    NotificationPreference, BLOOD_TYPE_CHOICES, PURPOSE_CHOICES
)


# User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    blood_type = forms.ChoiceField(choices=[('', 'Select Blood Type')] + BLOOD_TYPE_CHOICES, required=False, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'blood_type', 'date_of_birth', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })


# Admin Registration Form
class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        user.is_staff = True
        if commit:
            user.save()
        return user


# Login Form
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


# Donor Registration Form
class DonorRegistrationForm(forms.ModelForm):
    blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'required': 'required'
    }))
    
    class Meta:
        model = Donor
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'blood_type', 
                  'date_of_birth', 'address', 'city', 'state']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
        }


# Blood Request Form
class BloodRequestForm(forms.ModelForm):
    blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'required': 'required'
    }))
    purpose = forms.ChoiceField(choices=PURPOSE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'required': 'required'
    }))
    
    class Meta:
        model = BloodRequest
        fields = ['patient_name', 'blood_type', 'units_needed', 'purpose', 'purpose_details',
                  'urgency', 'hospital_name', 'hospital_address', 'contact_number', 
                  'required_date', 'notes']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient Name'}),
            'units_needed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of Units', 'min': '1'}),
            'purpose_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional details about the purpose (optional)'}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}),
            'hospital_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Hospital Address'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'required_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional Notes (optional)'}),
        }


# Blood Donation Form
class BloodDonationForm(forms.ModelForm):
    blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'required': 'required'
    }))
    
    class Meta:
        model = BloodDonation
        fields = ['donor', 'donation_date', 'units_donated', 'blood_type', 'hospital_name', 'notes']
        widgets = {
            'donor': forms.Select(attrs={'class': 'form-control'}),
            'donation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'units_donated': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes (optional)'}),
        }


# Blood Request Status Update Form
class BloodRequestStatusForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



# ============================================
# INVENTORY MANAGEMENT FORMS
# ============================================

# Blood Unit Form
class BloodUnitForm(forms.ModelForm):
    """Form for adding individual blood units to inventory"""
    blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'required': 'required'
    }))
    
    class Meta:
        model = BloodUnit
        fields = ['blood_type', 'donation', 'donation_date', 'expiration_date', 
                  'unit_number', 'volume_ml', 'storage_location', 'notes']
        widgets = {
            'donation': forms.Select(attrs={'class': 'form-control'}),
            'donation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'unit_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique Unit Number'}),
            'volume_ml': forms.NumberInput(attrs={'class': 'form-control', 'value': '450', 'min': '1'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Storage Location (optional)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-calculate expiration date (42 days from donation)
        if not self.instance.pk and 'donation_date' in self.initial:
            from datetime import timedelta
            self.initial['expiration_date'] = (
                self.initial['donation_date'] + timedelta(days=42)
            )


# Inventory Threshold Form - DISABLED (requires database migration)
# class InventoryThresholdForm(forms.ModelForm):
#     """Form for configuring inventory thresholds"""
#     class Meta:
#         model = BloodInventory
#         fields = ['minimum_threshold', 'critical_threshold', 'optimal_level']
#         widgets = {
#             'minimum_threshold': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': '1',
#                 'placeholder': 'Minimum Threshold'
#             }),
#             'critical_threshold': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': '1',
#                 'placeholder': 'Critical Threshold'
#             }),
#             'optimal_level': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': '1',
#                 'placeholder': 'Optimal Level'
#             }),
#         }



class NotificationPreferenceForm(forms.ModelForm):
    """Form for user notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'sms_enabled',
            'urgent_blood_email', 'urgent_blood_sms',
            'appointment_reminder_email', 'appointment_reminder_sms',
            'appointment_confirmation_email', 'appointment_confirmation_sms',
            'request_status_email', 'request_status_sms',
            'low_stock_email', 'low_stock_sms',
        ]
        
        widgets = {
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'urgent_blood_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'urgent_blood_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appointment_reminder_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appointment_reminder_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appointment_confirmation_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appointment_confirmation_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'request_status_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'request_status_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'low_stock_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'low_stock_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'email_enabled': 'Enable Email Notifications',
            'sms_enabled': 'Enable SMS Notifications',
            'urgent_blood_email': 'Urgent Blood Needs',
            'urgent_blood_sms': 'Urgent Blood Needs',
            'appointment_reminder_email': 'Appointment Reminders',
            'appointment_reminder_sms': 'Appointment Reminders',
            'appointment_confirmation_email': 'Booking Confirmations',
            'appointment_confirmation_sms': 'Booking Confirmations',
            'request_status_email': 'Request Status Updates',
            'request_status_sms': 'Request Status Updates',
            'low_stock_email': 'Low Stock Alerts (Admin)',
            'low_stock_sms': 'Low Stock Alerts (Admin)',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Hide admin-only fields for non-admin users
        if user and user.role != 'admin':
            self.fields.pop('low_stock_email', None)
            self.fields.pop('low_stock_sms', None)
