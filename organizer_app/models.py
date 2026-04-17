from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active / Live'),
        ('correction', 'Needs Correction'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('other', 'Other'),
    ]

    organizer = models.ForeignKey(User, on_delete=models.CASCADE, 
                                   related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    department = models.CharField(max_length=100)
    venue = models.CharField(max_length=200)
    event_date = models.DateField()
    event_time = models.TimeField()
    registration_deadline = models.DateField()
    max_capacity = models.IntegerField(default=100)
    team_event = models.BooleanField(default=False)
    min_team_size = models.IntegerField(default=1)
    max_team_size = models.IntegerField(default=1)
    tags = models.CharField(max_length=300, blank=True, help_text='Comma separated tags')
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True, help_text='Note from admin for correction/rejection')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

 
    def registered_count(self):
        return self.registrations.filter(status='confirmed').count()

    def is_open(self):
        from django.utils import timezone
        import datetime
        return self.status == 'active' and self.registration_deadline >= timezone.now().date()

    def get_tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class EventCoordinator(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='coordinators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='Coordinator')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Announcement(models.Model):
    PRIORITY_CHOICES = [('urgent', 'Urgent'), ('normal', 'Normal'), ('info', 'Info')]
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    sent_to = models.CharField(max_length=100, default='all')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
