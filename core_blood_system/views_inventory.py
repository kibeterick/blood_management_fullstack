"""
Inventory Management Views
Handles inventory dashboard, blood unit management, and expiration tracking
"""
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q

from .models import BloodInventory, BloodUnit, BloodDonation, BLOOD_TYPE_CHOICES
from .forms import BloodUnitForm, InventoryThresholdForm
from .inventory_manager import InventoryManager


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def inventory_dashboard(request):
    """Main inventory dashboard with real-time data and charts"""
    # Get inventory status
    status = InventoryManager.get_inventory_status()
    
    # Prepare chart data
    inventory = status['inventory']
    chart_data = {
        'labels': [inv.blood_type for inv in inventory],
        'quantities': [inv.units_available for inv in inventory],
        'thresholds': [inv.minimum_threshold for inv in inventory],
        'critical_thresholds': [getattr(inv, 'critical_threshold', 2) for inv in inventory],
        'statuses': [inv.get_status() for inv in inventory],
    }
    
    context = {
        'inventory': inventory,
        'expiring_soon': status['expiring_soon'],
        'expired_units': status['expired'],
        'low_stock': status['low_stock'],
        'critical_stock': status['critical_stock'],
        'total_units': status['total_units'],
        'chart_data': chart_data,
        'page_title': 'Blood Inventory Dashboard',
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def add_blood_unit(request):
    """Add new blood unit to inventory"""
    if request.method == 'POST':
        form = BloodUnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            
            # Update inventory count
            inventory, created = BloodInventory.objects.get_or_create(
                blood_type=unit.blood_type,
                defaults={'units_available': 0, 'minimum_threshold': 5}
            )
            inventory.units_available = BloodUnit.objects.filter(
                blood_type=unit.blood_type,
                status='available'
            ).count()
            inventory.save()
            
            messages.success(request, f'Blood unit {unit.unit_number} added successfully')
            return redirect('inventory_dashboard')
    else:
        form = BloodUnitForm()
    
    context = {
        'form': form,
        'page_title': 'Add Blood Unit',
    }
    return render(request, 'inventory/add_unit.html', context)


@login_required
@user_passes_test(is_admin)
def expiration_list(request):
    """View all units sorted by expiration date"""
    today = date.today()
    
    units = BloodUnit.objects.filter(status='available').order_by('expiration_date')
    
    # Categorize units
    expired = units.filter(expiration_date__lt=today)
    expiring_soon = units.filter(
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=7)
    )
    good = units.filter(expiration_date__gt=today + timedelta(days=7))
    
    context = {
        'expired': expired,
        'expiring_soon': expiring_soon,
        'good': good,
        'page_title': 'Blood Unit Expiration',
    }
    return render(request, 'inventory/expiration_list.html', context)


@login_required
@user_passes_test(is_admin)
def configure_thresholds(request):
    """Configure inventory thresholds for all blood types"""
    if request.method == 'POST':
        blood_type = request.POST.get('blood_type')
        inventory = get_object_or_404(BloodInventory, blood_type=blood_type)
        form = InventoryThresholdForm(request.POST, instance=inventory)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Thresholds updated for {blood_type}')
            return redirect('configure_thresholds')
    
    # Get all inventory items
    inventory_items = BloodInventory.objects.all()
    
    # Create forms for each blood type
    forms = []
    for inv in inventory_items:
        forms.append({
            'blood_type': inv.blood_type,
            'form': InventoryThresholdForm(instance=inv),
            'current_units': inv.units_available,
            'status': inv.get_status(),
        })
    
    context = {
        'forms': forms,
        'page_title': 'Configure Inventory Thresholds',
    }
    return render(request, 'inventory/configure_thresholds.html', context)


@login_required
def inventory_api(request):
    """JSON API for real-time inventory data"""
    inventory = BloodInventory.objects.all()
    data = [{
        'blood_type': inv.blood_type,
        'units_available': inv.units_available,
        'status': inv.get_status(),
        'threshold': inv.minimum_threshold,
        'critical_threshold': getattr(inv, 'critical_threshold', 2),
        'optimal_level': getattr(inv, 'optimal_level', 20),
        'last_updated': inv.last_updated.isoformat(),
    } for inv in inventory]
    
    return JsonResponse({'inventory': data})


@login_required
@user_passes_test(is_admin)
def mark_unit_used(request, unit_id):
    """Mark a blood unit as used"""
    unit = get_object_or_404(BloodUnit, id=unit_id)
    
    if unit.status != 'available':
        messages.error(request, f'Unit {unit.unit_number} is not available')
        return redirect('expiration_list')
    
    success = InventoryManager.use_blood_unit(unit.unit_number)
    
    if success:
        messages.success(request, f'Unit {unit.unit_number} marked as used')
    else:
        messages.error(request, f'Failed to mark unit {unit.unit_number} as used')
    
    return redirect('expiration_list')


@login_required
@user_passes_test(is_admin)
def mark_unit_expired(request, unit_id):
    """Manually mark a blood unit as expired"""
    unit = get_object_or_404(BloodUnit, id=unit_id)
    
    if unit.status != 'available':
        messages.error(request, f'Unit {unit.unit_number} is not available')
        return redirect('expiration_list')
    
    unit.status = 'expired'
    unit.save()
    
    # Update inventory count
    inventory = BloodInventory.objects.filter(blood_type=unit.blood_type).first()
    if inventory:
        inventory.units_available = BloodUnit.objects.filter(
            blood_type=unit.blood_type,
            status='available'
        ).count()
        inventory.save()
    
    messages.success(request, f'Unit {unit.unit_number} marked as expired')
    return redirect('expiration_list')


@login_required
@user_passes_test(is_admin)
def unit_detail(request, unit_id):
    """View details of a specific blood unit"""
    unit = get_object_or_404(BloodUnit, id=unit_id)
    
    context = {
        'unit': unit,
        'page_title': f'Blood Unit {unit.unit_number}',
    }
    return render(request, 'inventory/unit_detail.html', context)
