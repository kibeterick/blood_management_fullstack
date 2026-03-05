"""
Inventory Management Utilities
Handles blood unit tracking, expiration management, and inventory updates
"""
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q
from .models import BloodUnit, BloodInventory, BloodDonation


class InventoryManager:
    """Centralized inventory management logic"""
    
    @staticmethod
    def update_inventory_from_donation(donation):
        """
        Update inventory when donation is approved
        Creates BloodUnit and updates BloodInventory counts
        """
        if donation.status != 'approved':
            return None
        
        # Create blood unit
        unit = BloodUnit.objects.create(
            blood_type=donation.blood_type,
            donation=donation,
            donation_date=donation.donation_date,
            expiration_date=donation.donation_date + timedelta(days=42),
            unit_number=f"BU-{donation.id}-{int(timezone.now().timestamp())}",
            volume_ml=450 * donation.units_donated,
            status='available'
        )
        
        # Update inventory count
        inventory, created = BloodInventory.objects.get_or_create(
            blood_type=donation.blood_type,
            defaults={'units_available': 0, 'minimum_threshold': 5}
        )
        
        # Recalculate available units
        inventory.units_available = BloodUnit.objects.filter(
            blood_type=donation.blood_type,
            status='available'
        ).count()
        inventory.save()
        
        # Check for low stock and send alert if needed
        if inventory.is_low_stock():
            # Check if we haven't sent an alert in the last 24 hours
            if not inventory.alert_sent_at or (timezone.now() - inventory.alert_sent_at).days >= 1:
                from .email_notifications import EmailNotificationService
                EmailNotificationService.send_low_stock_alert(inventory)
                inventory.alert_sent_at = timezone.now()
                inventory.save()
        
        return unit
    
    @staticmethod
    def mark_expired_units():
        """
        Mark expired units (run as scheduled task)
        Returns count of units marked as expired
        """
        today = date.today()
        
        # Find and mark expired units
        expired_count = BloodUnit.objects.filter(
            status='available',
            expiration_date__lt=today
        ).update(status='expired')
        
        # Update inventory counts for affected blood types
        if expired_count > 0:
            from .models import BLOOD_TYPE_CHOICES
            for blood_type_tuple in BLOOD_TYPE_CHOICES:
                blood_type = blood_type_tuple[0]
                inventory = BloodInventory.objects.filter(blood_type=blood_type).first()
                if inventory:
                    inventory.units_available = BloodUnit.objects.filter(
                        blood_type=blood_type,
                        status='available'
                    ).count()
                    inventory.save()
        
        return expired_count
    
    @staticmethod
    def use_blood_unit(unit_number):
        """
        Mark a blood unit as used and decrement inventory
        Returns True if successful, False otherwise
        """
        try:
            unit = BloodUnit.objects.get(unit_number=unit_number, status='available')
            unit.status = 'used'
            unit.save()
            
            # Update inventory count
            inventory = BloodInventory.objects.filter(blood_type=unit.blood_type).first()
            if inventory:
                inventory.units_available = BloodUnit.objects.filter(
                    blood_type=unit.blood_type,
                    status='available'
                ).count()
                inventory.save()
            
            return True
        except BloodUnit.DoesNotExist:
            return False
    
    @staticmethod
    def get_expiring_units(days=7):
        """
        Get units expiring within specified days
        Default is 7 days
        """
        cutoff_date = date.today() + timedelta(days=days)
        return BloodUnit.objects.filter(
            status='available',
            expiration_date__lte=cutoff_date,
            expiration_date__gte=date.today()
        ).order_by('expiration_date')
    
    @staticmethod
    def get_expired_units():
        """Get all expired units that are still marked as available"""
        return BloodUnit.objects.filter(
            status='available',
            expiration_date__lt=date.today()
        ).order_by('expiration_date')
    
    @staticmethod
    def get_inventory_status():
        """
        Get comprehensive inventory status
        Returns dict with inventory data and alerts
        """
        inventory = BloodInventory.objects.all()
        expiring_soon = InventoryManager.get_expiring_units()
        expired = InventoryManager.get_expired_units()
        
        low_stock_items = []
        critical_stock_items = []
        
        for inv in inventory:
            status = inv.get_status()
            if status == 'critical':
                critical_stock_items.append(inv)
            elif status == 'low':
                low_stock_items.append(inv)
        
        return {
            'inventory': inventory,
            'expiring_soon': expiring_soon,
            'expired': expired,
            'low_stock': low_stock_items,
            'critical_stock': critical_stock_items,
            'total_units': sum(inv.units_available for inv in inventory),
        }
