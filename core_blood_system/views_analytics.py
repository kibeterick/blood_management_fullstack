"""
Feature 4: Advanced Analytics Dashboard
Views for analytics and reporting
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Donor, BloodRequest, BloodDonation, BloodInventory, CustomUser
from .enhancements import get_dashboard_analytics, get_monthly_trends
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


@login_required
def analytics_dashboard(request):
    """Advanced analytics dashboard (Admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can access analytics.')
        return redirect('user_dashboard')
    
    # Get comprehensive analytics
    analytics = get_dashboard_analytics()
    
    # Get date range from request
    date_range = request.GET.get('range', '30')  # Default 30 days
    
    context = {
        'analytics': analytics,
        'date_range': date_range,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def get_chart_data(request):
    """API endpoint for chart data"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    chart_type = request.GET.get('type', 'monthly_trends')
    
    if chart_type == 'monthly_trends':
        data = get_monthly_trends(6)
        return JsonResponse({'data': data})
    
    elif chart_type == 'blood_type_distribution':
        distribution = Donor.objects.values('blood_type').annotate(
            count=Count('id')
        ).order_by('-count')
        return JsonResponse({'data': list(distribution)})
    
    elif chart_type == 'request_status':
        status_data = BloodRequest.objects.values('status').annotate(
            count=Count('id')
        )
        return JsonResponse({'data': list(status_data)})
    
    elif chart_type == 'donation_status':
        donation_data = BloodDonation.objects.values('status').annotate(
            count=Count('id')
        )
        return JsonResponse({'data': list(donation_data)})
    
    return JsonResponse({'error': 'Invalid chart type'}, status=400)


@login_required
def export_analytics_report(request):
    """Export analytics report as PDF"""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can export reports.')
        return redirect('user_dashboard')
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from django.http import HttpResponse
    import io
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=analytics_report.pdf'
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Blood Management System - Analytics Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Get analytics
    analytics = get_dashboard_analytics()
    
    # Summary table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Donors', str(analytics['total_donors'])],
        ['Active Donors', str(analytics['active_donors'])],
        ['Total Requests', str(analytics['total_requests'])],
        ['Pending Requests', str(analytics['pending_requests'])],
        ['Total Donations', str(analytics['total_donations'])],
        ['Total Units Donated', str(analytics['total_units_donated'])],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Footer
    footer_text = f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
