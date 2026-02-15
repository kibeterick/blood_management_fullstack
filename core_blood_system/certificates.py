"""
Donation Certificate Generator
Generate beautiful PDF certificates for blood donors
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import os


def generate_donation_certificate(donation):
    """
    Generate a professional donation certificate PDF
    """
    buffer = BytesIO()
    
    # Create PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Certificate Border
    p.setStrokeColor(colors.HexColor('#dc3545'))
    p.setLineWidth(3)
    p.rect(0.5*inch, 0.5*inch, width-inch, height-inch, stroke=1, fill=0)
    
    # Inner Border
    p.setStrokeColor(colors.HexColor('#c82333'))
    p.setLineWidth(1)
    p.rect(0.6*inch, 0.6*inch, width-1.2*inch, height-1.2*inch, stroke=1, fill=0)
    
    # Header - Certificate Title
    p.setFont("Helvetica-Bold", 36)
    p.setFillColor(colors.HexColor('#dc3545'))
    p.drawCentredString(width/2, height-1.5*inch, "CERTIFICATE")
    
    p.setFont("Helvetica", 24)
    p.setFillColor(colors.HexColor('#6c757d'))
    p.drawCentredString(width/2, height-1.9*inch, "of Blood Donation")
    
    # Decorative Line
    p.setStrokeColor(colors.HexColor('#dc3545'))
    p.setLineWidth(2)
    p.line(2*inch, height-2.2*inch, width-2*inch, height-2.2*inch)
    
    # "This is to certify that"
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.black)
    p.drawCentredString(width/2, height-2.8*inch, "This is to certify that")
    
    # Donor Name (Large and Bold)
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(colors.HexColor('#dc3545'))
    donor_name = f"{donation.donor.first_name} {donation.donor.last_name}"
    p.drawCentredString(width/2, height-3.4*inch, donor_name)
    
    # Decorative underline for name
    name_width = p.stringWidth(donor_name, "Helvetica-Bold", 28)
    p.setStrokeColor(colors.HexColor('#dc3545'))
    p.setLineWidth(1)
    p.line(width/2 - name_width/2, height-3.5*inch, 
           width/2 + name_width/2, height-3.5*inch)
    
    # Donation Details
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.black)
    
    y_position = height - 4.2*inch
    
    details_text = [
        f"has generously donated {donation.units_donated} unit(s) of {donation.blood_type} blood",
        f"on {donation.donation_date.strftime('%B %d, %Y')}",
        f"at {donation.hospital_name}"
    ]
    
    for text in details_text:
        p.drawCentredString(width/2, y_position, text)
        y_position -= 0.4*inch
    
    # Appreciation Message
    p.setFont("Helvetica-Oblique", 16)
    p.setFillColor(colors.HexColor('#198754'))
    p.drawCentredString(width/2, height-5.8*inch, 
                       "Your selfless act of kindness has the power to save lives.")
    p.drawCentredString(width/2, height-6.2*inch, 
                       "Thank you for being a hero!")
    
    # Blood Drop Icon (Text-based)
    p.setFont("Helvetica-Bold", 48)
    p.setFillColor(colors.HexColor('#dc3545'))
    p.drawCentredString(width/2, height-7.2*inch, "♥")
    
    # Certificate Number
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor('#6c757d'))
    cert_number = f"Certificate No: BMS-{donation.id:06d}"
    p.drawString(1*inch, 1.2*inch, cert_number)
    
    # Issue Date
    issue_date = f"Issued on: {timezone.now().strftime('%B %d, %Y')}"
    p.drawRightString(width-1*inch, 1.2*inch, issue_date)
    
    # Signature Line
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(width-3*inch, 1.8*inch, width-1*inch, 1.8*inch)
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width-2*inch, 1.6*inch, "Authorized Signature")
    
    # Footer
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.HexColor('#6c757d'))
    p.drawCentredString(width/2, 0.8*inch, "Blood Management System")
    p.drawCentredString(width/2, 0.6*inch, "Saving Lives Through Blood Donation")
    
    # Finalize PDF
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer


def download_donation_certificate(request, donation_id):
    """
    View to download donation certificate
    """
    from .models import BloodDonation
    from django.contrib.auth.decorators import login_required
    
    try:
        donation = BloodDonation.objects.get(id=donation_id)
        
        # Generate certificate
        pdf_buffer = generate_donation_certificate(donation)
        
        # Create response
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"Blood_Donation_Certificate_{donation.donor.last_name}_{donation.donation_date}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except BloodDonation.DoesNotExist:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Donation record not found.')
        return redirect('user_dashboard')


def generate_donor_appreciation_card(donor):
    """
    Generate a thank you card for donors
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(6*inch, 4*inch))
    width, height = (6*inch, 4*inch)
    
    # Background
    p.setFillColor(colors.HexColor('#f8f9fa'))
    p.rect(0, 0, width, height, stroke=0, fill=1)
    
    # Border
    p.setStrokeColor(colors.HexColor('#dc3545'))
    p.setLineWidth(2)
    p.rect(0.2*inch, 0.2*inch, width-0.4*inch, height-0.4*inch, stroke=1, fill=0)
    
    # Title
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.HexColor('#dc3545'))
    p.drawCentredString(width/2, height-0.8*inch, "Thank You!")
    
    # Donor Name
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(colors.black)
    p.drawCentredString(width/2, height-1.3*inch, 
                       f"{donor.first_name} {donor.last_name}")
    
    # Message
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.HexColor('#495057'))
    
    messages_text = [
        "Your generous blood donation",
        "has the power to save lives.",
        "",
        "You are a true hero!",
    ]
    
    y_pos = height - 1.8*inch
    for msg in messages_text:
        p.drawCentredString(width/2, y_pos, msg)
        y_pos -= 0.25*inch
    
    # Blood Type Badge
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor('#dc3545'))
    p.drawCentredString(width/2, 0.6*inch, f"Blood Type: {donor.blood_type}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
