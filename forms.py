from django import forms
from .models import Donor

class DonorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name', 'email', 'phone', 'blood_group', 'age']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}),
            # Add more styling classes as needed
        }