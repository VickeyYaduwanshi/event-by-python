from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from organizer_app.models import Event, Announcement
from .models import Registration, Certificate, EventFeedback
from accounts.models import UserProfile

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?role=student')
        try:
            if request.user.profile.role != 'student':
                messages.error(request, 'Access denied.')
                return redirect('/')
        except UserProfile.DoesNotExist:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

@student_required
def dashboard(request):
    registrations = Registration.objects.filter(student=request.user, status='confirmed').select_related('event').order_by('event__event_date')
    certificates = Certificate.objects.filter(student=request.user).select_related('event').order_by('-issued_at')
    announcements = Announcement.objects.all().order_by('-created_at')[:5]
    
    from django.utils import timezone
    upcoming = registrations.filter(event__event_date__gte=timezone.now().date())
    past = registrations.filter(event__event_date__lt=timezone.now().date())
    
    context = {
        'registrations': registrations,
        'upcoming': upcoming,
        'past': past,
        'certificates': certificates,
        'announcements': announcements,
        'total_events': registrations.count(),
        'total_certs': certificates.count(),
    }
    return render(request, 'student/dashboard.html', context)

@student_required
def discover_events(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    events = Event.objects.filter(status='active').order_by('event_date')
    if category:
        events = events.filter(category=category)
    if search:
        events = events.filter(title__icontains=search) | events.filter(description__icontains=search)
    
    registered_ids = Registration.objects.filter(student=request.user, status='confirmed').values_list('event_id', flat=True)
    
    return render(request, 'student/discover.html', {
        'events': events,
        'registered_ids': list(registered_ids),
        'category': category,
        'search': search,
    })

@student_required
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk, status='active')
    
    if Registration.objects.filter(student=request.user, event=event).exists():
        messages.info(request, 'Already registered!')
        return redirect('student_dashboard')
    
    if event.registered_count() >= event.max_capacity:
        messages.error(request, 'Event is full.')
        return redirect('discover_events')
    
    if request.method == 'POST':
        reg = Registration.objects.create(
            student=request.user,
            event=event,
            team_name=request.POST.get('team_name', ''),
            team_members=request.POST.get('team_members', ''),
            status='confirmed',
        )
        messages.success(request, f'Successfully registered! Ticket: #{reg.ticket_number}')
        return redirect('my_ticket', pk=reg.pk)
    
    return render(request, 'student/register_event.html', {'event': event})

@student_required
def my_ticket(request, pk):
    reg = get_object_or_404(Registration, pk=pk, student=request.user)
    return render(request, 'student/ticket.html', {'registration': reg})

@student_required
def my_events(request):
    from django.utils import timezone
    regs = Registration.objects.filter(student=request.user).select_related('event').order_by('event__event_date')
    upcoming = regs.filter(event__event_date__gte=timezone.now().date(), status='confirmed')
    past = regs.filter(event__event_date__lt=timezone.now().date())
    return render(request, 'student/my_events.html', {'upcoming': upcoming, 'past': past})

@student_required
def certificates(request):
    certs = Certificate.objects.filter(student=request.user).select_related('event').order_by('-issued_at')
    return render(request, 'student/certificates.html', {'certificates': certs})

@student_required
def cancel_registration(request, pk):
    reg = get_object_or_404(Registration, pk=pk, student=request.user)
    reg.status = 'cancelled'
    reg.save()
    messages.success(request, 'Registration cancelled.')
    return redirect('my_events')

@student_required
def submit_feedback(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if not Registration.objects.filter(student=request.user, event=event).exists():
        messages.error(request, 'You are not registered for this event.')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        feedback, created = EventFeedback.objects.get_or_create(
            student=request.user, event=event,
            defaults={
                'rating': int(request.POST.get('rating', 3)),
                'content_quality': int(request.POST.get('content_quality', 3)),
                'organization': int(request.POST.get('organization', 3)),
                'comment': request.POST.get('comment', ''),
            }
        )
        if not created:
            feedback.rating = int(request.POST.get('rating', 3))
            feedback.content_quality = int(request.POST.get('content_quality', 3))
            feedback.organization = int(request.POST.get('organization', 3))
            feedback.comment = request.POST.get('comment', '')
            feedback.save()
        messages.success(request, 'Feedback submitted!')
        return redirect('student_dashboard')
    
    return render(request, 'student/feedback.html', {'event': event})
