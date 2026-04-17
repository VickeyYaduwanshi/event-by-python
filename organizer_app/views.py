from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Event, Announcement
from student_app.models import Registration, Certificate
from accounts.models import UserProfile

def organizer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?role=organizer')
        try:
            if request.user.profile.role != 'organizer':
                messages.error(request, 'Access denied.')
                return redirect('/')
        except UserProfile.DoesNotExist:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

@organizer_required
def dashboard(request):
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    total = events.count()
    active = events.filter(status='active').count()
    pending = events.filter(status='pending').count()
    total_registrations = Registration.objects.filter(event__organizer=request.user, status='confirmed').count()
    recent_events = events[:5]
    announcements = Announcement.objects.filter(organizer=request.user).order_by('-created_at')[:5]
    
    # Category breakdown
    cats = {}
    for e in events.filter(status='active'):
        cats[e.category] = cats.get(e.category, 0) + e.registered_count()
    
    context = {
        'total_events': total,
        'active_events': active,
        'pending_events': pending,
        'total_registrations': total_registrations,
        'recent_events': recent_events,
        'announcements': announcements,
        'category_stats': cats,
        'events': events,
    }
    return render(request, 'organizer/dashboard.html', context)

@organizer_required
def create_event(request):
    if request.method == 'POST':
        event = Event(
            organizer  =request.user,
            title      =request.POST.get('title'),
            description=request.POST.get('description'),
            category   =request.POST.get('category'),
            department =request.POST.get('department'),
            venue      =request.POST.get('venue'),
            event_date =request.POST.get('event_date'),
            event_time =request.POST.get('event_time'),
            registration_deadline=request.POST.get('registration_deadline'),
            max_capacity   =int(request.POST.get('max_capacity', 100)),
            team_event     =request.POST.get('team_event') == 'on',
            min_team_size  =int(request.POST.get('min_team_size', 1)),
            max_team_size  =int(request.POST.get('max_team_size', 1)),
            tags=request.POST.get('tags', ''),
            status='pending',
        )
        if request.FILES.get('poster'):
            event.poster = request.FILES['poster']
        event.save()
        messages.success(request, 'Event submitted for admin approval!')
        return redirect('organizer_dashboard')
    return render(request, 'organizer/create_event.html')

@organizer_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    if event.status == 'active':
        messages.error(request, 'Cannot edit an active event. Contact admin.')
        return redirect('organizer_dashboard')
    
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.category = request.POST.get('category')
        event.department = request.POST.get('department')
        event.venue = request.POST.get('venue')
        event.event_date = request.POST.get('event_date')
        event.event_time = request.POST.get('event_time')
        event.registration_deadline = request.POST.get('registration_deadline')
        event.max_capacity = int(request.POST.get('max_capacity', 100))
        event.team_event = request.POST.get('team_event') == 'on'
        event.tags = request.POST.get('tags', '')
        if request.FILES.get('poster'):
            event.poster = request.FILES['poster']
        event.status = 'pending'
        event.admin_note = ''
        event.save()
        messages.success(request, 'Event resubmitted for approval!')
        return redirect('organizer_dashboard')
    return render(request, 'organizer/edit_event.html', {'event': event})

@organizer_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    registrations = Registration.objects.filter(event=event, status='confirmed').select_related('student', 'student__profile')
    checked_in = registrations.filter(checked_in=True).count()
    return render(request, 'organizer/event_detail.html', {
        'event': event,
        'registrations': registrations,
        'checked_in': checked_in,
    })

@organizer_required
def checkin_student(request, reg_pk):
    from django.utils import timezone
    reg = get_object_or_404(Registration, pk=reg_pk, event__organizer=request.user)
    reg.checked_in = True
    reg.checked_in_at = timezone.now()
    reg.save()
    messages.success(request, f'{reg.student.get_full_name()} checked in!')
    return redirect('event_detail', pk=reg.event.pk)

@organizer_required
def send_announcement(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        event = None
        if event_id:
            event = Event.objects.filter(pk=event_id, organizer=request.user).first()
        ann = Announcement.objects.create(
            organizer=request.user,
            event=event,
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
            priority=request.POST.get('priority', 'normal'),
            sent_to=request.POST.get('sent_to', 'all'),
        )
        messages.success(request, 'Announcement sent!')
        return redirect('organizer_dashboard')
    events = Event.objects.filter(organizer=request.user, status='active')
    return render(request, 'organizer/announcement.html', {'events': events})

@organizer_required
def issue_certificate(request, reg_pk):
    reg = get_object_or_404(Registration, pk=reg_pk, event__organizer=request.user)
    cert_type = request.POST.get('cert_type', 'participation')
    cert, created = Certificate.objects.get_or_create(
        student=reg.student, event=reg.event, cert_type=cert_type
    )
    if created:
        messages.success(request, f'Certificate issued to {reg.student.get_full_name()}!')
    else:
        messages.info(request, 'Certificate already issued.')
    return redirect('event_detail', pk=reg.event.pk)

@organizer_required
def analytics(request):
    from django.db.models import Count
    events = Event.objects.filter(organizer=request.user)
    data = []
    for e in events:
        data.append({
            'event': e,
            'reg_count': e.registered_count(),
            'checked_in': Registration.objects.filter(event=e, checked_in=True).count(),
        })
    return render(request, 'organizer/analytics.html', {'events_data': data})
