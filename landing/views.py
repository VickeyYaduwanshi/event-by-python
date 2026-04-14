from django.shortcuts import render
from organizer_app.models import Event

def home(request):
    featured_events = Event.objects.filter(status='active').order_by('-created_at')[:6]
    stats = {
        'total_events': Event.objects.filter(status='active').count(),
        'total_students': 0,
        'total_organizers': 0,
    }
    try:
        from django.contrib.auth.models import User
        from accounts.models import UserProfile
        stats['total_students'] = UserProfile.objects.filter(role='student').count()
        stats['total_organizers'] = UserProfile.objects.filter(role='organizer').count()
    except Exception:
        pass
    return render(request, 'landing/home.html', {'featured_events': featured_events, 'stats': stats})
