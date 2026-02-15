from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Donor, BloodRequest, BloodDonation, BLOOD_TYPE_CHOICES, PURPOSE_CHOICES


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