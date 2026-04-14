from django.db import models
from django.contrib.auth.models import User
from organizer_app.models import Event

class Registration(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlist', 'Waitlist'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    team_name = models.CharField(max_length=100, blank=True)
    team_members = models.TextField(blank=True, help_text='Comma separated roll numbers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    registered_at = models.DateTimeField(auto_now_add=True)
    ticket_number = models.CharField(max_length=20, unique=True)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'event')

    def __str__(self):
        return f"{self.student.username} - {self.event.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import random, string
            self.ticket_number = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)


class Certificate(models.Model):
    CERT_TYPE_CHOICES = [
        ('participation', 'Participation'),
        ('winner_1', '1st Place'),
        ('winner_2', '2nd Place'),
        ('winner_3', '3rd Place'),
        ('organizer', 'Organizer'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    cert_type = models.CharField(max_length=20, choices=CERT_TYPE_CHOICES)
    issued_at = models.DateTimeField(auto_now_add=True)
    cert_number = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.student.username} - {self.event.title} ({self.cert_type})"

    def save(self, *args, **kwargs):
        if not self.cert_number:
            import random, string
            self.cert_number = 'CERT-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)


class EventFeedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    content_quality = models.IntegerField(default=3)
    organization = models.IntegerField(default=3)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'event')

    def __str__(self):
        return f"{self.student.username} - {self.event.title} ({self.rating}★)"
