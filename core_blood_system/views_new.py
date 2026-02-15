from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import CustomUser, Donor, BloodRequest, BloodDonation, BloodInventory
from .forms import (UserRegistrationForm, AdminRegistrationForm, CustomLoginForm, 
                    DonorRegistrationForm, BloodRequestForm, BloodDonationForm,
                    BloodRequestStatusForm)


# Home Page
def home(request):
    """Home page view"""
    return render(request, 'home.html')


# User Registration
def user_register(request):
    """Regular user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user'
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/user_register.html', {'form': form})


# Admin Registration
def admin_register(request):
    """Admin registration - should be restricted in production"""
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Admin account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'registration/admin_register.html', {'form': form})


# Login View
def user_login(request):
    """User login"""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect based on user role
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


# Logout View
@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# User Dashboard
@login_required
def user_dashboard(request):
    """Dashboard for regular users"""
    user_requests = BloodRequest.objects.filter(requester=request.user)
    return render(request, 'dashboard/user_dashboard.html', {
        'user_requests': user_requests
    })


# Admin Dashboard
@login_required
def admin_dashboard(request):
    """Dashboard for administrators"""
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('user_dashboard')
    
    # Get statistics
    total_donors = Donor.objects.count()
    total_requests = BloodRequest.objects.count()
    pending_requests = BloodRequest.objects.filter(status='pending').count()
    total_donations = BloodDonation.objects.count()
    
    # Get recent requests
    recent_requests = BloodRequest.objects.all()[:10]
    
    # Get blood inventory
    inventory = BloodInventory.objects.all()
    
    context = {
        'total_donors': total_donors,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'total_donations': total_donations,
        'recent_requests': recent_requests,
        'inventory': inventory,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


# Donor Registration
@login_required
def register_donor(request):
    """Register a new donor"""
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            messages.success(request, 'Donor registered successfully!')
            return redirect('donor_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill with user data if available
        initial_data = {}
        if request.user.first_name:
            initial_data['first_name'] = request.user.first_name
        if request.user.last_name:
            initial_data['last_name'] = request.user.last_name
        if request.user.email:
            initial_data['email'] = request.user.email
        if request.user.phone_number:
            initial_data['phone_number'] = request.user.phone_number
        if request.user.blood_type:
            initial_data['blood_type'] = request.user.blood_type
        
        form = DonorRegistrationForm(initial=initial_data)
    
    return render(request, 'donors/register_donor.html', {'form': form})


# Donor List
@login_required
def donor_list(request):
    """List all donors with search and filter"""
    donors = Donor.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        donors = donors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Filter by blood type
    blood_type_filter = request.GET.get('blood_type', '')
    if blood_type_filter:
        donors = donors.filter(blood_type=blood_type_filter)
    
    # Filter by availability
    availability_filter = request.GET.get('availability', '')
    if availability_filter:
        donors = donors.filter(is_available=(availability_filter == 'available'))
    
    context = {
        'donors': donors,
        'search_query': search_query,
        'blood_type_filter': blood_type_filter,
        'availability_filter': availability_filter,
    }
    
    return render(request, 'donors/donor_list.html', context)


# Request Blood
@login_required
def request_blood(request):
    """Create a new blood request"""
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()
            messages.success(request, 'Blood request submitted successfully!')
            return redirect('blood_request_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BloodRequestForm()
    
    return render(request, 'requests/request_blood.html', {'form': form})


# Blood Request List
@login_required
def blood_request_list(request):
    """List all blood requests"""
    if request.user.role == 'admin':
        requests = BloodRequest.objects.all()
    else:
        requests = BloodRequest.objects.filter(requester=request.user)
    
    # Filter by blood type
    blood_type_filter = request.GET.get('blood_type', '')
    if blood_type_filter:
        requests = requests.filter(blood_type=blood_type_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    # Filter by purpose
    purpose_filter = request.GET.get('purpose', '')