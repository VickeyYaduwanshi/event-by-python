from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create default admin user and sample data'

    def handle(self, *args, **kwargs):
        # Create admin user
        if not User.objects.filter(username='user-219').exists():
            admin = User.objects.create_superuser(
                username='user-219',
                email='admin@campus.edu',
                password='8120',
                first_name='Campus',
                last_name='Admin'
            )
            UserProfile.objects.create(user=admin, role='admin', department='Administration')
            self.stdout.write(self.style.SUCCESS('✅ Admin user created: user-219 / 8120'))
        else:
            self.stdout.write('Admin user already exists.')
            # Ensure profile exists
            admin = User.objects.get(username='user-219')
            UserProfile.objects.get_or_create(user=admin, defaults={'role': 'admin', 'department': 'Administration'})

        # Create sample organizer
        if not User.objects.filter(username='organizer1').exists():
            org = User.objects.create_user(
                username='organizer1',
                email='organizer@campus.edu',
                password='org123',
                first_name='Rahul',
                last_name='Kumar'
            )
            UserProfile.objects.create(user=org, role='organizer', department='CSE', phone='9876543210')
            self.stdout.write(self.style.SUCCESS('✅ Sample organizer: organizer1 / org123'))

        # Create sample student
        if not User.objects.filter(username='student1').exists():
            stu = User.objects.create_user(
                username='student1',
                email='student@campus.edu',
                password='stu123',
                first_name='Ananya',
                last_name='Sharma'
            )
            UserProfile.objects.create(user=stu, role='student', department='CSE', roll_number='21CS088', phone='9876500001')
            self.stdout.write(self.style.SUCCESS('✅ Sample student: student1 / stu123'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Initial setup complete!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin:     user-219  / 8120')
        self.stdout.write('  Organizer: organizer1 / org123')
        self.stdout.write('  Student:   student1   / stu123')
