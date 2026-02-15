from django.core.management.base import BaseCommand
from core_blood_system.models import CustomUser


class Command(BaseCommand):
    help = 'Create a superuser for the blood management system'

    def handle(self, *args, **options):
        # Create default admin if doesn't exist
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@bloodbank.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                blood_type='O+'
            )
            self.stdout.write(self.style.SUCCESS('✅ Superuser "admin" created successfully!'))
            self.stdout.write(self.style.WARNING('Username: admin'))
            self.stdout.write(self.style.WARNING('Password: admin123'))
            self.stdout.write(self.style.WARNING('Please change the password after first login!'))
        else:
            self.stdout.write(self.style.WARNING('Superuser "admin" already exists!'))
        
        # Fix permissions for all users with role='admin'
        admin_users = CustomUser.objects.filter(role='admin')
        fixed_count = 0
        for user in admin_users:
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Fixed permissions for user: {user.username}'))
        
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Fixed {fixed_count} admin user(s) permissions!'))
        
        # Show all admin users
        self.stdout.write('\n📋 Current admin users:')
        for user in CustomUser.objects.filter(role='admin'):
            status = '✅' if (user.is_staff and user.is_superuser) else '❌'
            self.stdout.write(f'   {status} {user.username} (staff: {user.is_staff}, superuser: {user.is_superuser})')
