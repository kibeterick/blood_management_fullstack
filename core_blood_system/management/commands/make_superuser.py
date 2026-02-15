from django.core.management.base import BaseCommand
from core_blood_system.models import CustomUser


class Command(BaseCommand):
    help = 'Make an existing user a superuser with full admin permissions'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make superuser')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = CustomUser.objects.get(username=username)
            
            # Set admin permissions
            user.is_staff = True
            user.is_superuser = True
            user.role = 'admin'
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ SUCCESS! User "{username}" now has full admin permissions:'))
            self.stdout.write(f'   - is_staff: {user.is_staff}')
            self.stdout.write(f'   - is_superuser: {user.is_superuser}')
            self.stdout.write(f'   - role: {user.role}')
            self.stdout.write(f'\nYou can now access Django admin at: http://127.0.0.1:8000/admin/')
            
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'\n❌ ERROR: User "{username}" not found!'))
            self.stdout.write('\nAvailable users:')
            for u in CustomUser.objects.all():
                self.stdout.write(f'   - {u.username} (role: {u.role}, staff: {u.is_staff}, superuser: {u.is_superuser})')
