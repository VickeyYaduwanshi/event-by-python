from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    roll_number = models.CharField(max_length=20, blank=True)
    enrollment_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_student(self):
        return self.role == 'student'

    def is_organizer(self):
        return self.role == 'organizer'

    def is_admin(self):
        return self.role == 'admin'
