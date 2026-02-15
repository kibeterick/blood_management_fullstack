from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Donor, Recipient

@receiver(post_save, sender=Donor)
def notify_admin_new_donor(sender, instance, created, **kwargs):
    if created:
        print(f"--- ADMIN NOTIFICATION: New Donor {instance.email} registered! ---")

@receiver(post_save, sender=Recipient)
def notify_admin_new_recipient(sender, instance, created, **kwargs):
    if created:
        print(f"--- ADMIN NOTIFICATION: New Request from {instance.hospital_name} ---")