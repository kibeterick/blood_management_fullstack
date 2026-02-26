"""
Feature 5: QR Code System
Views for QR code generation and verification
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import QRCode, Donor, BloodDonation, DonationAppointment
from .enhancements import generate_qr_code, verify_qr_code


@login_required
def generate_donor_qr(request, donor_id):
    """Generate QR code for a donor"""
    donor = get_object_or_404(Donor, id=donor_id)
    
    # Check permission
    if request.user.role != 'admin' and (not hasattr(request.user, 'donor') or donor != request.user.donor):
        messages.error(request, 'You do not have permission to generate this QR code.')
        return redirect('user_dashboard')
    
    # Check if QR code already exists
    existing_qr = QRCode.objects.filter(qr_type='donor', donor=donor).first()
    
    if not existing_qr:
        # Generate new QR code
        qr_data = {
            'donor_id': donor.id,
            'name': f"{donor.first_name} {donor.last_name}",
            'blood_type': donor.blood_type,
            'email': donor.email,
        }
        qr_code = generate_qr_code('donor', donor, qr_data)
    else:
        qr_code = existing_qr
    
    context = {
        'qr_code': qr_code,
        'donor': donor,
    }
    
    return render(request, 'qr_codes/donor_qr.html', context)


@login_required
def generate_certificate_qr(request, donation_id):
    """Generate QR code for a donation certificate"""
    donation = get_object_or_404(BloodDonation, id=donation_id)
    
    # Check permission
    if request.user.role != 'admin' and donation.donor.user != request.user:
        messages.error(request, 'You do not have permission to generate this QR code.')
        return redirect('user_dashboard')
    
    # Check if QR code already exists
    existing_qr = QRCode.objects.filter(qr_type='certificate', donation=donation).first()
    
    if not existing_qr:
        # Generate new QR code
        qr_data = {
            'donation_id': donation.id,
            'donor_name': f"{donation.donor.first_name} {donation.donor.last_name}",
            'blood_type': donation.blood_type,
            'units': donation.units_donated,
            'date': donation.donation_date.strftime('%Y-%m-%d'),
        }
        qr_code = generate_qr_code('certificate', donation, qr_data)
    else:
        qr_code = existing_qr
    
    context = {
        'qr_code': qr_code,
        'donation': donation,
    }
    
    return render(request, 'qr_codes/certificate_qr.html', context)


@login_required
def qr_scanner(request):
    """QR code scanner page"""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can scan QR codes.')
        return redirect('user_dashboard')
    
    return render(request, 'qr_codes/scanner.html')


@login_required
def verify_qr(request):
    """Verify a QR code"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        code = request.POST.get('code', '')
        
        result = verify_qr_code(code)
        
        if result['valid']:
            qr_code = result['qr_code']
            data = result['data']
            
            response_data = {
                'valid': True,
                'type': qr_code.qr_type,
                'data': data,
                'scanned_count': qr_code.scanned_count,
                'last_scanned': qr_code.last_scanned.strftime('%Y-%m-%d %H:%M') if qr_code.last_scanned else None,
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({'valid': False, 'error': result['error']})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def download_qr_image(request, qr_id):
    """Download QR code image"""
    qr_code = get_object_or_404(QRCode, id=qr_id)
    
    # Check permission
    if request.user.role != 'admin':
        if qr_code.donor and qr_code.donor.user != request.user:
            messages.error(request, 'You do not have permission to download this QR code.')
            return redirect('user_dashboard')
    
    if qr_code.qr_image:
        response = HttpResponse(qr_code.qr_image.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{qr_code.code}.png"'
        return response
    else:
        messages.error(request, 'QR code image not found.')
        return redirect('user_dashboard')


@login_required
def my_qr_codes(request):
    """View all QR codes for the current user"""
    qr_codes = []
    
    # Get donor QR codes
    if hasattr(request.user, 'donor'):
        donor_qrs = QRCode.objects.filter(donor=request.user.donor)
        qr_codes.extend(donor_qrs)
    
    context = {
        'qr_codes': qr_codes,
    }
    
    return render(request, 'qr_codes/my_qr_codes.html', context)
