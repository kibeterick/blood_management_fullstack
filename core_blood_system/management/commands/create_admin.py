from django.core.management.base import BaseCommand
from core_blood_system.models import CustomUser


class Command(BaseCommand):
    help = 'Create a superuser for the blood management system'

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@bloodbank.com',
                password='admin123',  # Change this password after first login!
                first_name='Admin',
                last_name='User',
                role='admin',
                blood_type='O+'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
            self.stdout.write(self.style.WARNING('Username: admin'))
            self.stdout.write(self.style.WARNING('Password: admin123'))
            self.stdout.write(self.style.WARNING('Please change the password after first login!'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists!'))
