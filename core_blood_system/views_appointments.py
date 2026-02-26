"""
Appointment Scheduling Views
Feature 1 of Top 5 Enhancements
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from .models import DonationAppointment, Donor, CustomUser
from .enhancements import get_available_time_slots, create_appointment


@login_required
def book_appointment(request):
    """Book a new donation appointment"""
    # Get or create donor for this user
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.warning(request, 'Please register as a donor first before booking an appointment.')
        return redirect('register_donor')
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        time_slot = request.POST.get('time_slot')
        location = request.POST.get('location')
        address = request.POST.get('address')
        notes = request.POST.get('notes', '')
        
        # Validate date is in future
        selected_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        if selected_date < timezone.now().date():
            messages.error(request, 'Please select a future date.')
            return redirect('book_appointment')
        
        # Check if slot is available
        available_slots = get_available_time_slots(selected_date, location)
        if time_slot not in available_slots:
            messages.error(request, 'This time slot is no longer available. Please choose another.')
            return redirect('book_appointment')
        
        # Create appointment
        try:
            appointment = create_appointment(
                donor=donor,
                user=request.user,
                date=selected_date,
                time_slot=time_slot,
                location=location,
                address=address,
                notes=notes
            )
            messages.success(request, f'Appointment booked successfully for {selected_date} at {time_slot}!')
            return redirect('my_appointments')
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
    
    # Get available locations
    locations = [
        {'name': 'City Hospital', 'address': '123 Main Street, City Center'},
        {'name': 'Community Blood Center', 'address': '456 Oak Avenue, Downtown'},
        {'name': 'Regional Medical Center', 'address': '789 Pine Road, Westside'},
    ]
    
    context = {
        'locations': locations,
        'min_date': timezone.now().date() + timedelta(days=1),  # Tomorrow onwards
        'time_slots': DonationAppointment.TIME_SLOT_CHOICES,
    }
    
    return render(request, 'appointments/book_appointment.html', context)


@login_required
def my_appointments(request):
    """View user's appointments"""
    try:
        donor = Donor.objects.get(user=request.user)
        appointments = DonationAppointment.objects.filter(
            donor=donor
        ).order_by('-appointment_date', '-time_slot')
    except Donor.DoesNotExist:
        appointments = []
    
    # Separate upcoming and past
    today = timezone.now().date()
    upcoming = [apt for apt in appointments if apt.appointment_date >= today and apt.status in ['scheduled', 'confirmed']]
    past = [apt for apt in appointments if apt.appointment_date < today or apt.status in ['completed', 'cancelled', 'no_show']]
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    }
    
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(DonationAppointment, id=appointment_id)
    
    # Check if user owns this appointment
    if appointment.user != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('my_appointments')
    
    # Check if can cancel (24 hours before)
    appointment_datetime = datetime.combine(appointment.appointment_date, datetime.min.time())
    hours_until = (appointment_datetime - datetime.now()).total_seconds() / 3600
    
    if hours_until < 24:
        messages.error(request, 'Cannot cancel appointment less than 24 hours before scheduled time.')
        return redirect('my_appointments')
    
    if appointment.status not in ['scheduled', 'confirmed']:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('my_appointments')
    
    appointment.status = 'cancelled'
    appointment.save()
    
    messages.success(request, 'Appointment cancelled successfully.')
    return redirect('my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    appointment = get_object_or_404(DonationAppointment, id=appointment_id)
    
    # Check if user owns this appointment
    if appointment.user != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        new_date = request.POST.get('appointment_date')
        new_time_slot = request.POST.get('time_slot')
        
        # Validate
        selected_date = datetime.strptime(new_date, '%Y-%m-%d').date()
        if selected_date < timezone.now().date():
            messages.error(request, 'Please select a future date.')
            return redirect('reschedule_appointment', appointment_id=appointment_id)
        
        # Check availability
        available_slots = get_available_time_slots(selected_date, appointment.location)
        if new_time_slot not in available_slots:
            messages.error(request, 'This time slot is not available.')
            return redirect('reschedule_appointment', appointment_id=appointment_id)
        
        # Update appointment
        appointment.appointment_date = selected_date
        appointment.time_slot = new_time_slot
        appointment.reminder_sent = False
        appointment.save()
        
        messages.success(request, 'Appointment rescheduled successfully!')
        return redirect('my_appointments')
    
    context = {
        'appointment': appointment,
        'min_date': timezone.now().date() + timedelta(days=1),
        'time_slots': DonationAppointment.TIME_SLOT_CHOICES,
    }
    
    return render(request, 'appointments/reschedule_appointment.html', context)


# ADMIN VIEWS

@login_required
def admin_appointments_list(request):
    """Admin view of all appointments"""
    if request.user.role != 'admin':
        messages.error(request, 'Admin access required.')
        return redirect('user_dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date', 'all')
    
    appointments = DonationAppointment.objects.all().select_related('donor', 'user')
    
    # Apply filters
    if status_filter != 'all':
        appointments = appointments.filter(status=status_filter)
    
    today = timezone.now().date()
    if date_filter == 'today':
        appointments = appointments.filter(appointment_date=today)
    elif date_filter == 'upcoming':
        appointments = appointments.filter(appointment_date__gte=today)
    elif date_filter == 'past':
        appointments = appointments.filter(appointment_date__lt=today)
    
    appointments = appointments.order_by('-appointment_date', '-time_slot')
    
    # Statistics
    stats = {
        'total': DonationAppointment.objects.count(),
        'scheduled': DonationAppointment.objects.filter(status='scheduled').count(),
        'confirmed': DonationAppointment.objects.filter(status='confirmed').count(),
        'completed': DonationAppointment.objects.filter(status='completed').count(),
        'today': DonationAppointment.objects.filter(appointment_date=today).count(),
    }
    
    context = {
        'appointments': appointments,
        'stats': stats,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    
    return render(request, 'appointments/admin_appointments_list.html', context)


@login_required
def admin_appointment_detail(request, appointment_id):
    """Admin view appointment details and update status"""
    if request.user.role != 'admin':
        messages.error(request, 'Admin access required.')
        return redirect('user_dashboard')
    
    appointment = get_object_or_404(DonationAppointment, id=appointment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm':
            appointment.status = 'confirmed'
            appointment.save()
            messages.success(request, 'Appointment confirmed.')
        elif action == 'complete':
            appointment.status = 'completed'
            appointment.save()
            messages.success(request, 'Appointment marked as completed.')
        elif action == 'no_show':
            appointment.status = 'no_show'
            appointment.save()
            messages.warning(request, 'Appointment marked as no-show.')
        elif action == 'cancel':
            appointment.status = 'cancelled'
            appointment.save()
            messages.info(request, 'Appointment cancelled.')
        
        return redirect('admin_appointment_detail', appointment_id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/admin_appointment_detail.html', context)


@login_required
def appointments_calendar(request):
    """Calendar view of appointments (admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Admin access required.')
        return redirect('user_dashboard')
    
    # Get month and year from query params
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Get appointments for this month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    appointments = DonationAppointment.objects.filter(
        appointment_date__gte=start_date,
        appointment_date__lt=end_date
    ).select_related('donor')
    
    # Group by date
    appointments_by_date = {}
    for apt in appointments:
        date_str = apt.appointment_date.strftime('%Y-%m-%d')
        if date_str not in appointments_by_date:
            appointments_by_date[date_str] = []
        appointments_by_date[date_str].append(apt)
    
    context = {
        'year': year,
        'month': month,
        'appointments_by_date': appointments_by_date,
        'month_name': datetime(year, month, 1).strftime('%B'),
    }
    
    return render(request, 'appointments/calendar.html', context)
