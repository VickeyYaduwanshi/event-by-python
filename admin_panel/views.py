from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from organizer_app.models import Event, Announcement
from student_app.models import Registration, Certificate
from accounts.models import UserProfile

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?role=admin')
        try:
            if request.user.profile.role != 'admin' and not request.user.is_superuser:
                messages.error(request, 'Admin access required.')
                return redirect('/')
        except UserProfile.DoesNotExist:
            if not request.user.is_superuser:
                return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def dashboard(request):
    total_events = Event.objects.count()
    pending_events = Event.objects.filter(status='pending').count()
    active_events = Event.objects.filter(status='active').count()
    total_students = UserProfile.objects.filter(role='student').count()
    total_organizers = UserProfile.objects.filter(role='organizer').count()
    total_registrations = Registration.objects.filter(status='confirmed').count()
    recent_pending = Event.objects.filter(status='pending').order_by('-created_at')[:5]
    all_events = Event.objects.all().order_by('-created_at')[:10]
    context = {
        'total_events': total_events,
        'pending_events': pending_events,
        'active_events': active_events,
        'total_students': total_students,
        'total_organizers': total_organizers,
        'total_registrations': total_registrations,
        'recent_pending': recent_pending,
        'all_events': all_events,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@admin_required
def pending_events(request):
    events = Event.objects.filter(status='pending').order_by('-created_at').select_related('organizer')
    return render(request, 'admin_panel/pending_events.html', {'events': events})

@admin_required
def all_events(request):
    status_filter = request.GET.get('status', '')
    events = Event.objects.all().order_by('-created_at').select_related('organizer')
    if status_filter:
        events = events.filter(status=status_filter)
    return render(request, 'admin_panel/all_events.html', {'events': events, 'status_filter': status_filter})

@admin_required
def review_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registrations = Registration.objects.filter(event=event).select_related('student')
    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('admin_note', '')
        if action == 'approve':
            event.status = 'active'
            event.admin_note = ''
            event.save()
            messages.success(request, f'Event "{event.title}" approved and is now LIVE!')
        elif action == 'correction':
            event.status = 'correction'
            event.admin_note = note
            event.save()
            messages.warning(request, f'Event sent back for correction.')
        elif action == 'reject':
            event.status = 'rejected'
            event.admin_note = note
            event.save()
            messages.error(request, f'Event rejected.')
        elif action == 'complete':
            event.status = 'completed'
            event.save()
            messages.success(request, 'Event marked as completed.')
        elif action == 'cancel':
            event.status = 'cancelled'
            event.save()
            messages.info(request, 'Event cancelled.')
        return redirect('admin_all_events')
    return render(request, 'admin_panel/review_event.html', {'event': event, 'registrations': registrations})

@admin_required
def manage_users(request):
    role_filter = request.GET.get('role', '')
    profiles = UserProfile.objects.all().select_related('user').order_by('-created_at')
    if role_filter:
        profiles = profiles.filter(role=role_filter)
    return render(request, 'admin_panel/manage_users.html', {'profiles': profiles, 'role_filter': role_filter})

@admin_required
def toggle_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} {status}.')
    return redirect('manage_users')

@admin_required
def admin_analytics(request):
    from django.db.models import Count
    events_by_cat = {}
    for cat, _ in Event.CATEGORY_CHOICES:
        events_by_cat[cat] = Event.objects.filter(category=cat).count()
    events_by_status = {}
    for st, _ in Event.STATUS_CHOICES:
        events_by_status[st] = Event.objects.filter(status=st).count()
    top_events = []
    for e in Event.objects.filter(status__in=['active','completed']):
        top_events.append({'event': e, 'count': e.registered_count()})
    top_events = sorted(top_events, key=lambda x: x['count'], reverse=True)[:5]
    context = {
        'events_by_cat': events_by_cat,
        'events_by_status': events_by_status,
        'top_events': top_events,
        'total_certs': Certificate.objects.count(),
    }
    return render(request, 'admin_panel/analytics.html', context)

@admin_required
def issue_cert_admin(request, reg_pk):
    reg = get_object_or_404(Registration, pk=reg_pk)
    cert_type = request.POST.get('cert_type', 'participation')
    cert, created = Certificate.objects.get_or_create(
        student=reg.student, event=reg.event, cert_type=cert_type
    )
    if created:
        messages.success(request, f'Certificate issued to {reg.student.get_full_name() or reg.student.username}!')
    else:
        messages.info(request, 'Certificate already exists.')
    return redirect('review_event', pk=reg.event.pk)
