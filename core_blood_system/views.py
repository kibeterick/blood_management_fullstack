from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, Donor, BloodRequest, BloodDonation, BloodInventory
from .forms import (UserRegistrationForm, AdminRegistrationForm, CustomLoginForm, 
                    DonorRegistrationForm, BloodRequestForm, BloodDonationForm,
                    BloodRequestStatusForm)

# Import for Excel/PDF exports
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io


# Home Page
def home(request):
    """Home page view"""
    return render(request, 'home.html')


def home_portal(request):
    """Home portal - redirect to home"""
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
    """Admin registration - restricted after first admin is created"""
    # Check if an admin already exists
    admin_exists = CustomUser.objects.filter(role='admin').exists()
    
    if admin_exists:
        messages.error(request, 'Admin registration is disabled. An administrator already exists. Please contact the existing admin for access.')
        return redirect('login')
    
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
    
    return render(request, 'admin_dashboard.html', context)


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
        if hasattr(request.user, 'first_name') and request.user.first_name:
            initial_data['first_name'] = request.user.first_name
        if hasattr(request.user, 'last_name') and request.user.last_name:
            initial_data['last_name'] = request.user.last_name
        if hasattr(request.user, 'email') and request.user.email:
            initial_data['email'] = request.user.email
        if hasattr(request.user, 'phone_number') and request.user.phone_number:
            initial_data['phone_number'] = request.user.phone_number
        if hasattr(request.user, 'blood_type') and request.user.blood_type:
            initial_data['blood_type'] = request.user.blood_type
        
        form = DonorRegistrationForm(initial=initial_data)
    
    return render(request, 'register_donor.html', {'form': form})


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
    
    return render(request, 'donor_list.html', context)


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
    
    return render(request, 'request_blood.html', {'form': form})


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
    if purpose_filter:
        requests = requests.filter(purpose=purpose_filter)
    
    # Filter by urgency
    urgency_filter = request.GET.get('urgency', '')
    if urgency_filter:
        requests = requests.filter(urgency=urgency_filter)
    
    context = {
        'requests': requests,
        'blood_type_filter': blood_type_filter,
        'status_filter': status_filter,
        'purpose_filter': purpose_filter,
        'urgency_filter': urgency_filter,
    }
    
    return render(request, 'all_requests.html', context)


def all_requests(request):
    """Alias for blood_request_list"""
    return blood_request_list(request)


# Delete Donor
@login_required
def delete_donor(request, pk):
    """Delete a donor"""
    donor = get_object_or_404(Donor, pk=pk)
    donor.delete()
    messages.success(request, 'Donor deleted successfully!')
    return redirect('donor_list')


# Stock Report
@login_required
def stock_report_print(request):
    """Print stock report"""
    inventory = BloodInventory.objects.all()
    return render(request, 'stock_report.html', {'inventory': inventory})


# Delete Request
@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_request(request, request_id):
    """Delete a blood request"""
    try:
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        blood_request.delete()
        return JsonResponse({"success": True, "message": "Deleted successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# ==========================================
# EXPORT FUNCTIONS
# ==========================================

# Export Donors to Excel
@login_required
def export_donors_excel(request):
    """Export donor list to Excel"""
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Donors List"
    
    # Add header with styling
    headers = ['#', 'First Name', 'Last Name', 'Blood Type', 'Email', 'Phone', 'City', 'State', 'Available', 'Last Donation']
    ws.append(headers)
    
    # Style header row
    header_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=12)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Get donors
    donors = Donor.objects.all()
    
    # Add data
    for idx, donor in enumerate(donors, start=1):
        ws.append([
            idx,
            donor.first_name,
            donor.last_name,
            donor.blood_type,
            donor.email,
            donor.phone_number,
            donor.city,
            donor.state,
            'Yes' if donor.is_available else 'No',
            donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else 'Never'
        ])
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=donors_list.xlsx'
    
    wb.save(response)
    return response


# Export Donors to PDF
@login_required
def export_donors_pdf(request):
    """Export donor list to PDF"""
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=donors_list.pdf'
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF0000'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    title = Paragraph("🩸 Blood Donors List", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Get donors
    donors = Donor.objects.all()
    
    # Create table data
    data = [['#', 'Name', 'Blood Type', 'Phone', 'City', 'Available']]
    
    for idx, donor in enumerate(donors, start=1):
        data.append([
            str(idx),
            f"{donor.first_name} {donor.last_name}",
            donor.blood_type,
            donor.phone_number,
            donor.city,
            '✓' if donor.is_available else '✗'
        ])
    
    # Create table
    table = Table(data, colWidths=[0.5*inch, 2*inch, 1*inch, 1.5*inch, 1.5*inch, 1*inch])
    
    # Style table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # Add footer
    elements.append(Spacer(1, 0.5 * inch))
    footer_text = f"Total Donors: {donors.count()} | Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


# Export Blood Requests to Excel
@login_required
def export_requests_excel(request):
    """Export blood requests to Excel"""
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Blood Requests"
    
    # Add header
    headers = ['#', 'Patient Name', 'Blood Type', 'Purpose', 'Units', 'Urgency', 'Hospital', 'Status', 'Date']
    ws.append(headers)
    
    # Style header
    header_fill = PatternFill(start_color='DC143C', end_color='DC143C', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=12)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Get requests
    if request.user.role == 'admin':
        requests = BloodRequest.objects.all()
    else:
        requests = BloodRequest.objects.filter(requester=request.user)
    
    # Add data
    for idx, req in enumerate(requests, start=1):
        ws.append([
            idx,
            req.patient_name,
            req.blood_type,
            req.get_purpose_display(),
            req.units_needed,
            req.get_urgency_display(),
            req.hospital_name,
            req.get_status_display(),
            req.created_at.strftime('%Y-%m-%d')
        ])
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=blood_requests.xlsx'
    
    wb.save(response)
    return response


# Export Blood Requests to PDF
@login_required
def export_requests_pdf(request):
    """Export blood requests to PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=blood_requests.pdf'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#DC143C'),
        spaceAfter=30,
        alignment=1
    )
    
    # Title
    title = Paragraph("🩸 Blood Requests Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Get requests
    if request.user.role == 'admin':
        requests = BloodRequest.objects.all()
    else:
        requests = BloodRequest.objects.filter(requester=request.user)
    
    # Create table
    data = [['#', 'Patient', 'Blood Type', 'Purpose', 'Units', 'Urgency', 'Status']]
    
    for idx, req in enumerate(requests, start=1):
        data.append([
            str(idx),
            req.patient_name,
            req.blood_type,
            req.get_purpose_display(),
            str(req.units_needed),
            req.get_urgency_display(),
            req.get_status_display()
        ])
    
    table = Table(data, colWidths=[0.4*inch, 1.5*inch, 0.8*inch, 1.2*inch, 0.6*inch, 0.9*inch, 1*inch])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.crimson),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # Footer
    elements.append(Spacer(1, 0.5 * inch))
    footer_text = f"Total Requests: {requests.count()} | Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


# ==========================================
# BLOOD TYPE COMPATIBILITY CHECKER - NEW FEATURE
# ==========================================

# Blood type compatibility data
BLOOD_COMPATIBILITY = {
    'A+': {
        'can_donate_to': ['A+', 'AB+'],
        'can_receive_from': ['A+', 'A-', 'O+', 'O-']
    },
    'A-': {
        'can_donate_to': ['A+', 'A-', 'AB+', 'AB-'],
        'can_receive_from': ['A-', 'O-']
    },
    'B+': {
        'can_donate_to': ['B+', 'AB+'],
        'can_receive_from': ['B+', 'B-', 'O+', 'O-']
    },
    'B-': {
        'can_donate_to': ['B+', 'B-', 'AB+', 'AB-'],
        'can_receive_from': ['B-', 'O-']
    },
    'AB+': {
        'can_donate_to': ['AB+'],
        'can_receive_from': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    },
    'AB-': {
        'can_donate_to': ['AB+', 'AB-'],
        'can_receive_from': ['A-', 'B-', 'AB-', 'O-']
    },
    'O+': {
        'can_donate_to': ['A+', 'B+', 'AB+', 'O+'],
        'can_receive_from': ['O+', 'O-']
    },
    'O-': {
        'can_donate_to': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'can_receive_from': ['O-']
    }
}


@login_required
def blood_compatibility_checker(request):
    """Blood type compatibility checker and donor finder"""
    selected_blood_type = request.GET.get('blood_type', '')
    compatible_donors = []
    compatibility_info = None
    
    if selected_blood_type and selected_blood_type in BLOOD_COMPATIBILITY:
        compatibility_info = BLOOD_COMPATIBILITY[selected_blood_type]
        
        # Find compatible donors
        compatible_blood_types = compatibility_info['can_receive_from']
        compatible_donors = Donor.objects.filter(
            blood_type__in=compatible_blood_types,
            is_available=True
        ).order_by('blood_type', 'city')
    
    context = {
        'selected_blood_type': selected_blood_type,
        'compatibility_info': compatibility_info,
        'compatible_donors': compatible_donors,
        'blood_compatibility': BLOOD_COMPATIBILITY,
    }
    
    return render(request, 'compatibility/blood_compatibility.html', context)


@login_required
def find_compatible_donors(request, blood_type):
    """Find donors compatible with a specific blood type"""
    if blood_type not in BLOOD_COMPATIBILITY:
        messages.error(request, 'Invalid blood type')
        return redirect('blood_compatibility_checker')
    
    compatibility_info = BLOOD_COMPATIBILITY[blood_type]
    compatible_blood_types = compatibility_info['can_receive_from']
    
    donors = Donor.objects.filter(
        blood_type__in=compatible_blood_types,
        is_available=True
    ).order_by('blood_type', 'city')
    
    context = {
        'blood_type': blood_type,
        'compatible_blood_types': compatible_blood_types,
        'donors': donors,
    }
    
    return render(request, 'compatibility/compatible_donors.html', context)