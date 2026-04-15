# 🎓 Campus Events Hub — Complete Project Guide (Hinglish)

Ek complete college event management system jisme 3 roles hain: Student, Organizer, Admin

## 🚀 Quick Setup

### 1. Install dependencies
```bash
cd college_events
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations accounts organizer_app student_app admin_panel
python manage.py migrate
```

### 3. Create initial data (admin + sample users)
```bash
python manage.py setup_initial_data
```

### 4. Run server
```bash
python manage.py runserver
```

### 5. Open in browser
```
http://127.0.0.1:8000/
```

---

## 🔑 Login Credentials

| Role      | Username   | Password |
|-----------|-----------|----------|
| Admin     | user-219  | 8120     |
| Organizer | organizer1 | org123   |
| Student   | student1  | stu123   |

---

---

# 📂 FOLDER RESPONSIBILITIES (KON SA FOLDER KYA KAAM KARTA HAI)

## 1. **college_events/** (Main Project Config)
- **settings.py** - Database config, installed apps, static files path
- **urls.py** - Main router jaha sab app ke URLs connect hote hain
- **wsgi.py** - Production me deploy karne ke liye

## 2. **accounts/** (Authentication & User Profile)
- **models.py** - `UserProfile` model (role, enrollment, department store karta hai)
- **views.py** - `login_view()`, `register_view()`, `logout_view()` functions
- **urls.py** - `/accounts/login/`, `/accounts/register/`, `/accounts/logout/` routes
- **templates/accounts/** - login.html, register.html UI pages

**Responsibility:** Sab users ko login/register/manage karna

## 3. **organizer_app/** (Event Creation & Management)
- **models.py** - `Event`, `Announcement`, `EventCoordinator` models (database tables)
- **views.py** - `create_event()`, `edit_event()`, `send_announcement()`, `checkin_student()`, `analytics()` functions
- **urls.py** - `/organizer/create/`, `/organizer/edit/<id>/`, `/organizer/checkin/` routes
- **templates/organizer/** - create_event.html, edit_event.html, announcement.html, analytics.html

**Responsibility:** Organizer ke liye event create/edit karna, attendance track karna, announcements send karna

## 4. **student_app/** (Registration & Participation)
- **models.py** - `Registration`, `Certificate`, `EventFeedback` models
- **views.py** - `discover_events()`, `register_event()`, `my_ticket()`, `submit_feedback()`, `certificates()` functions
- **urls.py** - `/student/discover/`, `/student/register/<id>/`, `/student/ticket/` routes
- **templates/student/** - discover.html, register_event.html, ticket.html, feedback.html

**Responsibility:** Students ke liye events browse, register, tickets, certificates, feedback

## 5. **admin_panel/** (Approvals & Analytics)
- **views.py** - `review_event()`, `manage_users()`, `admin_analytics()`, `toggle_user()` functions
- **urls.py** - `/admin-panel/pending/`, `/admin-panel/users/`, `/admin-panel/analytics/` routes
- **templates/admin_panel/** - pending_events.html, review_event.html, manage_users.html, analytics.html

**Responsibility:** Events approve/reject, users manage, platform analytics dekhna

## 6. **landing/** (Home Page)
- **views.py** - `home()` function jo featured events aur stats display karta hai
- **templates/landing/** - home.html page

## 7. **templates/** (All UI Pages)
- **base.html** - Master template (sidebar, topbar, CSS load)
- **accounts/**, **organizer/**, **student/**, **admin_panel/** - Role-specific pages
- **includes/** - Reusable components (sidebars)

## 8. **static/css/** (Styling)
- **base.css** - Global styles (colors, buttons, forms, layout)
- **accounts/login.css**, **accounts/register.css** - Login/register specific styles
- **landing/home.css** - Home page specific styles

## 9. **db.sqlite3** (Database)
- SQLite database jisme sab data store hota hai (users, events, registrations, certificates)

---

# 🔑 LOGIN/REGISTER FLOW - CODE & DATA DETAILED

## Registration Process (Naya user kaise add hota hai)

**URL Route:** `POST /accounts/register/`

**Code Flow (`accounts/views.py` - `register_view()` function):**

```python
# Line 100-146: register_view() function
def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')  # 'student' ya 'organizer'
        email = request.POST.get('email')
        name = request.POST.get('name')
        
        # Validation: Passwords match?
        if password != password2:
            return render(register.html) with error
        
        # Create User object (Django's built-in)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        
        # Create UserProfile (custom profile with role)
        UserProfile.objects.create(
            user=user,
            role='student',  # or 'organizer'
            enrollment_number=enrollment,
            department=department
        )
```

**Database Storage:**
- **Django User Table** - username, email, password (hashed)
- **UserProfile Table** - role, enrollment_number, department, branch

**Template (`accounts/register.html`):**
- Form fields: Name, Email, Department, Branch, Password
- Conditional fields: Enrollment Number (students only)
- CSS: `static/css/accounts/register.css` se styling

---

## Login Process (User kaise login karta hai)

**URL Route:** `GET/POST /accounts/login/?role=student`

**Code Flow (`accounts/views.py` - `login_view()` function, Line 10-78):**

```python
def login_view(request):
    role = request.GET.get('role', 'student')  # URL param se role
    
    if request.method == 'POST':
        password = request.POST.get('password')
        
        # STUDENT LOGIN (enrollment number)
        if role == 'student':
            enrollment = request.POST.get('username')
            profile = UserProfile.objects.get(
                enrollment_number=enrollment, 
                role='student'
            )
            user = profile.user
            if user.check_password(password):
                login(request, user)  # Django session create
                return redirect_by_role(user)
        
        # ORGANIZER LOGIN (Gmail)
        elif role == 'organizer':
            email = request.POST.get('username')
            user = User.objects.get(email=email)
            if profile.role == 'organizer' and user.check_password(password):
                login(request, user)
                return redirect_by_role(user)
        
        # ADMIN LOGIN (hardcoded)
        elif role == 'admin':
            username_input = request.POST.get('username')
            if username_input == 'user-219' and password == '8120':
                admin_user = User.objects.get_or_create(
                    username='admin_user',
                    defaults={'is_superuser': True, 'is_staff': True}
                )
                login(request, admin_user)
                return redirect('/admin-panel/dashboard/')
```

**Database Query:**
```python
# Student: UserProfile.objects.get(enrollment_number=X) → User.check_password()
# Organizer: User.objects.get(email=X) → User.check_password()
# Admin: Hardcoded check (username='user-219', password='8120')
```

**Session Storage:**
- Django `request.session` me user ID store hota hai
- Browser cookie me session ID store hota hai

---

# 📋 PAGES - DATA FLOW DETAILED

## HOME PAGE (/)

**File:** `landing/views.py` - `home()` function (Line 4-20)

```python
def home(request):
    # Database se data fetch karna
    featured_events = Event.objects.filter(
        status='active'
    ).order_by('-created_at')[:6]  # 6 recent active events
    
    stats = {
        'total_events': Event.objects.filter(status='active').count(),
        'total_students': UserProfile.objects.filter(role='student').count(),
        'total_organizers': UserProfile.objects.filter(role='organizer').count(),
    }
    
    # Data template ko pass karna
    return render(request, 'landing/home.html', {
        'featured_events': featured_events,
        'stats': stats
    })
```

**UI Display (`landing/home.html`):**
- Featured events cards show hote hain (`.event-card`)
- Stats display: Total events, students, organizers
- CSS: `static/css/landing/home.css` se styling

**Database Tables Used:** Event, UserProfile

---

## STUDENT - DISCOVER EVENTS PAGE (/student/discover/)

**File:** `student_app/views.py` - `discover_events()` function (Line 25-45)

```python
def discover_events(request):
    category = request.GET.get('category', '')  # URL filter
    search = request.GET.get('search', '')
    
    # Base query: Sirf active events jo admin ne approve kiye
    events = Event.objects.filter(status='active').order_by('event_date')
    
    # Filters apply karna
    if category:
        events = events.filter(category=category)
    
    if search:
        events = events.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Check karna konse events student ne register kiye
    registered_ids = Registration.objects.filter(
        student=request.user,
        status='confirmed'
    ).values_list('event_id', flat=True)
    
    return render(request, 'student/discover.html', {
        'events': events,
        'registered_ids': list(registered_ids),
    })
```

**SQL Queries:**
```sql
-- Active events fetch
SELECT * FROM organizer_app_event WHERE status='active'

-- Student ka registrations check
SELECT event_id FROM student_app_registration 
WHERE student_id=X AND status='confirmed'
```

**UI Display (`student/discover.html`):**
- Events grid with cards
- "Already Registered" badge on registered events
- CSS: `static/css/base.css` grid classes

---

## ORGANIZER - CREATE EVENT PAGE (/organizer/create/)

**File:** `organizer_app/views.py` - `create_event()` function (Line 39-74)

```python
@organizer_required  # Decorator: only organizer access
def create_event(request):
    if request.method == 'POST':
        # Form data collect karna
        event = Event.objects.create(
            organizer=request.user,  # Current logged-in user
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
            department=request.POST.get('department'),
            venue=request.POST.get('venue'),
            event_date=request.POST.get('event_date'),
            event_time=request.POST.get('event_time'),
            registration_deadline=request.POST.get('registration_deadline'),
            max_capacity=int(request.POST.get('max_capacity', 100)),
            team_event=request.POST.get('team_event') == 'on',
            tags=request.POST.get('tags', ''),
            status='pending',  # Admin approval waiting
            poster=request.FILES['poster']  # Image upload
        )
        event.save()  # Database me insert
        return redirect('organizer_dashboard')
    
    return render(request, 'organizer/create_event.html')
```

**Database Storage:**
```python
# Event table me naya row add hota hai
event = Event(
    organizer_id=request.user.id,  # Foreign key
    title='Python Workshop',
    status='pending',  # Status lifecycle: pending → active/correction → completed
    poster_url='media/event_posters/xxxxx.jpg'
)
```

**File Upload:**
- Image `media/event_posters/` folder me save hota hai
- Database me path store hota hai

---

## ADMIN - PENDING EVENTS REVIEW (/admin-panel/pending/)

**File:** `admin_panel/views.py` - `review_event()` function (Line 58-103)

```python
@admin_required  # Only admins access kar sakte hain
def review_event(request, pk):
    event = Event.objects.get(pk=pk)  # Event khoj karna
    registrations = Registration.objects.filter(
        event=event
    ).select_related('student')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('admin_note', '')
        
        if action == 'approve':
            event.status = 'active'  # Database update
            event.admin_note = ''
            event.save()
            # Ab students ko ye event dikhega discover page pe
        
        elif action == 'correction':
            event.status = 'correction'
            event.admin_note = note  # Admin ka message save
            event.save()
            # Organizer ko notification (email future me add kar sakte ho)
        
        elif action == 'reject':
            event.status = 'rejected'
            event.admin_note = note
            event.save()
```

**Database Update:**
```sql
UPDATE organizer_app_event 
SET status='active', admin_note='' 
WHERE id=X
```

---

## STUDENT - MY EVENTS (/student/my-events/)

**File:** `student_app/views.py` - `my_events()` function (Line 85-95)

```python
@student_required
def my_events(request):
    from django.utils import timezone
    
    # Student ke sab registrations fetch karo
    regs = Registration.objects.filter(
        student=request.user
    ).select_related('event').order_by('event__event_date')
    
    # Upcoming aur Past events separate karo
    today = timezone.now().date()
    upcoming = regs.filter(
        event__event_date__gte=today,
        status='confirmed'
    )
    past = regs.filter(
        event__event_date__lt=today
    )
    
    return render(request, 'student/my_events.html', {
        'upcoming': upcoming,
        'past': past
    })
```

**Database Joins:**
```sql
SELECT * FROM student_app_registration 
WHERE student_id=X 
JOIN organizer_app_event ON event_id=event.id
ORDER BY event.event_date
```

**UI Display:**
- Upcoming events (blue badge)
- Past events (gray badge)
- "View Ticket" button → `/student/ticket/<registration_id>/`
- "Give Feedback" button → `/student/feedback/<event_id>/`

---

# ✅ REGISTRATION FLOW - FUNCTION BY FUNCTION

## Step 1: Student discover kare → register_event()

**URL:** `POST /student/register/<event_id>/`

**File:** `student_app/views.py` - Line 48-77

```python
@student_required
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk, status='active')
    
    # Check 1: Already registered?
    if Registration.objects.filter(
        student=request.user, 
        event=event
    ).exists():
        messages.error('Already registered!')
        return redirect('student_dashboard')
    
    # Check 2: Event full?
    if event.registered_count() >= event.max_capacity:
        messages.error('Event is full.')
        return redirect('discover_events')
    
    # Check 3: Create registration
    if request.method == 'POST':
        reg = Registration.objects.create(
            student=request.user,
            event=event,
            team_name=request.POST.get('team_name', ''),
            team_members=request.POST.get('team_members', ''),
            status='confirmed'
            # ticket_number auto-generate hota hai save() me
        )
        messages.success(f'Registered! Ticket: #{reg.ticket_number}')
        return redirect('my_ticket', pk=reg.pk)
```

**Database Tables:**
- **Registration table** me naya row: student_id, event_id, status='confirmed', ticket_number

---

## Step 2: Organizer attendance mark kare → checkin_student()

**URL:** `POST /organizer/checkin/<registration_id>/`

**File:** `organizer_app/views.py` - Line 125-133

```python
@organizer_required
def checkin_student(request, reg_pk):
    from django.utils import timezone
    
    reg = Registration.objects.get(pk=reg_pk, event__organizer=request.user)
    
    reg.checked_in = True
    reg.checked_in_at = timezone.now()  # Current timestamp
    reg.save()  # Database update
    
    messages.success(f'{reg.student.get_full_name()} checked in!')
    return redirect('event_detail', pk=reg.event.pk)
```

**Database Update:**
```sql
UPDATE student_app_registration 
SET checked_in=True, checked_in_at='2024-04-14 15:30:00' 
WHERE id=X
```

---

## Step 3: Certificate issue kare → issue_certificate()

**URL:** `POST /organizer/certificate/<registration_id>/`

**File:** `organizer_app/views.py` - Line 178-188

```python
@organizer_required
def issue_certificate(request, reg_pk):
    reg = Registration.objects.get(pk=reg_pk, event__organizer=request.user)
    
    cert_type = request.POST.get('cert_type', 'participation')
    
    cert, created = Certificate.objects.get_or_create(
        student=reg.student,
        event=reg.event,
        cert_type=cert_type  # 'participation', 'winner_1', 'winner_2', etc.
    )
    
    if created:
        # Naya certificate create hua
        messages.success(f'Certificate issued!')
    else:
        # Certificate pehle se existence hai
        messages.info('Certificate already exists.')
```

**Database Tables:**
- **Certificate table** me naya row: student_id, event_id, cert_type, cert_number (auto-generated)

---

# 🎟️ TICKET QR FLOW

**URL:** `GET /student/ticket/<registration_id>/`

**File:** `student_app/views.py` - Line 98-101

```python
@student_required
def my_ticket(request, pk):
    reg = get_object_or_404(
        Registration, 
        pk=pk, 
        student=request.user
    )
    
    return render(request, 'student/ticket.html', {
        'registration': reg
    })
```

**Template (`student/ticket.html`):**
- Displays: Student name, Event name, Ticket number (6 digits)
- QR code generated from: registration_id + ticket_number
- Function: Organizer scan kare ya manually ticket number enter kare checkin ke liye

---

# 📊 ORGANIZER ANALYTICS - FUNCTION BY FUNCTION

**URL:** `GET /organizer/analytics/`

**File:** `organizer_app/views.py` - Line 192-205

```python
@organizer_required
def analytics(request):
    # Organizer ke sab events fetch karo
    events = Event.objects.filter(organizer=request.user)
    
    data = []
    for e in events:
        data.append({
            'event': e,
            'reg_count': e.registered_count(),  # Total registrations
            'checked_in': Registration.objects.filter(
                event=e, 
                checked_in=True
            ).count()  # Attendance
        })
    
    return render(request, 'organizer/analytics.html', {
        'events_data': data
    })
```

**Database Queries:**
```sql
-- Total registrations
SELECT COUNT(*) FROM student_app_registration 
WHERE event_id=X AND status='confirmed'

-- Checked-in count
SELECT COUNT(*) FROM student_app_registration 
WHERE event_id=X AND checked_in=True
```

---

# 👥 ADMIN ANALYTICS

**URL:** `GET /admin-panel/analytics/`

**File:** `admin_panel/views.py` - Line 114-142

```python
@admin_required
def admin_analytics(request):
    # Events by category breakdown
    events_by_cat = {}
    for cat, _ in Event.CATEGORY_CHOICES:
        events_by_cat[cat] = Event.objects.filter(
            category=cat
        ).count()
    
    # Events by status breakdown
    events_by_status = {}
    for st, _ in Event.STATUS_CHOICES:
        events_by_status[st] = Event.objects.filter(
            status=st
        ).count()
    
    # Top 5 most registered events
    top_events = []
    for e in Event.objects.filter(status__in=['active', 'completed']):
        top_events.append({
            'event': e,
            'count': e.registered_count()
        })
    top_events = sorted(top_events, key=lambda x: x['count'], reverse=True)[:5]
    
    context = {
        'events_by_cat': events_by_cat,
        'events_by_status': events_by_status,
        'top_events': top_events,
        'total_certs': Certificate.objects.count()
    }
```

**Database Aggregations:**
```sql
-- Total certificates
SELECT COUNT(*) FROM student_app_certificate

-- Events by status
SELECT status, COUNT(*) FROM organizer_app_event GROUP BY status
```

---

# 💬 FEEDBACK FLOW

**URL:** `POST /student/feedback/<event_id>/`

**File:** `student_app/views.py` - Line 116-145

```python
@student_required
def submit_feedback(request, event_pk):
    event = Event.objects.get(pk=event_pk)
    
    # Check: Student ne event ke liye register kiya tha?
    if not Registration.objects.filter(
        student=request.user, 
        event=event
    ).exists():
        messages.error('Not registered for this event.')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        feedback, created = EventFeedback.objects.get_or_create(
            student=request.user,
            event=event,
            defaults={
                'rating': int(request.POST.get('rating', 3)),
                'content_quality': int(request.POST.get('content_quality', 3)),
                'organization': int(request.POST.get('organization', 3)),
                'comment': request.POST.get('comment', '')
            }
        )
        
        if not created:
            # Feedback pehle se hai, update karo
            feedback.rating = int(request.POST.get('rating'))
            feedback.save()
        
        messages.success('Feedback submitted!')
        return redirect('student_dashboard')
```

**Database Table:**
- **EventFeedback table**: student_id, event_id, rating (1-5), content_quality, organization, comment

**Constraints:**
- `unique_together = ('student', 'event')` - Ek student ek event ke liye sirf ek feedback dae sakta hai

---

# 🔐 DECORATORS (Authorization)

**File:** All views files me decorator use hote hain

```python
# accounts/views.py, organizer_app/views.py, etc.

def admin_required(view_func):
    """Admin ke liye pages protect karna"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?role=admin')
        if request.user.profile.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Admin access required.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def organizer_required(view_func):
    """Organizer ke liye pages protect karna"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?role=organizer')
        if request.user.profile.role != 'organizer':
            messages.error(request, 'Access denied.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    """Student ke liye pages protect karna"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?role=student')
        if request.user.profile.role != 'student':
            messages.error(request, 'Access denied.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

# 🗄️ DATABASE MODELS - DATA STRUCTURE

## User (Django Built-in)
```
id, username, email, password(hashed), is_active, is_staff, is_superuser
```

## UserProfile (Custom)
```
id, user_id (FK), role, enrollment_number, department, branch, phone, bio
Unique: enrollment_number
```

## Event (organizer_app)
```
id, organizer_id (FK User), title, description, category
status (pending/active/correction/rejected/completed), poster_url
event_date, event_time, registration_deadline, max_capacity
team_event, min_team_size, max_team_size, admin_note
```

## Registration (student_app)
```
id, student_id (FK User), event_id (FK Event)
team_name, team_members, status (confirmed/cancelled)
ticket_number (unique 6-digit), checked_in (boolean), checked_in_at
Unique: (student_id, event_id)
```

## Certificate (student_app)
```
id, student_id (FK User), event_id (FK Event)
cert_type (participation/winner_1/winner_2/winner_3)
cert_number (unique CERT-XXXXXXXX), issued_at
```

## EventFeedback (student_app)
```
id, student_id (FK User), event_id (FK Event)
rating (1-5), content_quality (1-5), organization (1-5)
comment, created_at
Unique: (student_id, event_id)
```

## Announcement (organizer_app)
```
id, organizer_id (FK User), event_id (FK Event, nullable)
subject, message, priority, sent_to, created_at
```

---

# 🔗 URL ROUTING MAP

```
/                              → landing.views.home() → home.html

/accounts/login/               → accounts.views.login_view() → login.html
/accounts/register/            → accounts.views.register_view() → register.html
/accounts/logout/              → accounts.views.logout_view() → redirect home

/student/dashboard/            → student_app.views.dashboard() → dashboard.html
/student/discover/             → student_app.views.discover_events() → discover.html
/student/register/<id>/        → student_app.views.register_event() → register_event.html
/student/ticket/<id>/          → student_app.views.my_ticket() → ticket.html
/student/my-events/            → student_app.views.my_events() → my_events.html
/student/certificates/         → student_app.views.certificates() → certificates.html
/student/feedback/<id>/        → student_app.views.submit_feedback() → feedback.html
/student/cancel/<id>/          → student_app.views.cancel_registration() → redirect my_events

/organizer/dashboard/          → organizer_app.views.dashboard() → dashboard.html
/organizer/create/             → organizer_app.views.create_event() → create_event.html
/organizer/edit/<id>/          → organizer_app.views.edit_event() → edit_event.html
/organizer/event/<id>/         → organizer_app.views.event_detail() → event_detail.html
/organizer/checkin/<id>/       → organizer_app.views.checkin_student() → redirect event_detail
/organizer/announce/           → organizer_app.views.send_announcement() → announcement.html
/organizer/certificate/<id>/   → organizer_app.views.issue_certificate() → redirect event_detail
/organizer/analytics/          → organizer_app.views.analytics() → analytics.html

/admin-panel/dashboard/        → admin_panel.views.dashboard() → dashboard.html
/admin-panel/pending/          → admin_panel.views.pending_events() → pending_events.html
/admin-panel/events/           → admin_panel.views.all_events() → all_events.html
/admin-panel/events/<id>/review/ → admin_panel.views.review_event() → review_event.html
/admin-panel/users/            → admin_panel.views.manage_users() → manage_users.html
/admin-panel/users/<id>/toggle/ → admin_panel.views.toggle_user() → redirect manage_users
/admin-panel/analytics/        → admin_panel.views.admin_analytics() → analytics.html
/admin-panel/cert/<id>/issue/  → admin_panel.views.issue_cert_admin() → redirect review_event
```

---

# 🎨 STATIC FILES & STYLING

**CSS Files:**
```
static/css/base.css              → Global styles, variables, layout
  - CSS Variables: --purple, --teal, --red, --amber, --pink, --gray
  - Classes: .btn, .btn-primary, .card, .badge, .form-control, .table
  - Layout: .sidebar, .main-content, .topbar, .layout

static/css/accounts/login.css    → Login form specific
  - .login-box, .role-tabs, .login-field-label

static/css/accounts/register.css → Register form specific
  - .reg-box, .grid-2

static/css/landing/home.css      → Home page specific
  - .hero, .hero-btns, .stats-bar, .events-grid, .event-card
```

**Template Inheritance:**
```
base.html (master)
  ├─ landing/home.html
  ├─ accounts/login.html, register.html
  ├─ admin_panel/*.html
  ├─ organizer/*.html
  └─ student/*.html
```

---

# 📱 SETUP & RUN

```bash
# Install dependencies
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Initial data (admin user setup)
python manage.py setup_initial_data

# Run server
python manage.py runserver

# Access: http://127.0.0.1:8000/
```

---

# 🔑 Test Login Credentials

| Role      | Input | Password |
|-----------|-------|----------|
| Admin     | 219 or user-219 | 8120 |
| Student   | enrollment_number | (jis user ko create kiya) |
| Organizer | email | (jis user ko create kiya) |

---

## ✨ Features

### 🔑 Admin
- Approve / Reject / Request Correction on events
- Manage all users (activate/deactivate)
- View platform analytics
- Issue certificates to participants

### 🎯 Organizer
- Create events (go to admin for approval first)
- Edit events sent for correction
- Live attendance tracker with check-in
- Send announcements to registered students
- Issue participation/winner certificates
- View event analytics

### 🎓 Student
- Browse & search active events
- Register for events (solo or team)
- View QR entry ticket
- Get checked in at events
- Download certificates
- Rate & give feedback on attended events

---

## 🔄 Event Flow

```
Organizer creates event
        ↓
   Status: PENDING
        ↓
  Admin reviews
    ↙        ↘
ACTIVE     CORRECTION / REJECTED
  ↓
Students register
  ↓
Organizer checks in students
  ↓
Admin/Organizer issues certificates
  ↓
Status: COMPLETED
```

---

## 🛠️ Tech Stack
- **Backend**: Django 4.2
- **Database**: SQLite
- **Auth**: Django built-in auth + custom UserProfile
- **Frontend**: Pure HTML/CSS (no external frameworks)
- **File storage**: Local media/ directory

---

---

# 📋 DETAILED FUNCTIONALITY FLOWS

## 1️⃣ AUTHENTICATION FLOW

### 1.1 User Data Model
**Files:** `accounts/models.py`

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User)  # Django's built-in User model
    role = models.CharField(choices=['student', 'organizer', 'admin'])
    enrollment_number = models.CharField()  # For students only
    department, branch, phone, bio  # Common fields
```

**Data Structure:**
- Each user has a Django `User` object (username, email, password)
- Each user has a custom `UserProfile` (role, enrollment, department, etc.)
- Role determines dashboard and permissions

---

### 1.2 Login Flow

**Route:** `GET/POST /accounts/login/?role={student|organizer|admin}`

**Files Involved:**
- `accounts/views.py` → `login_view()` function
- `templates/accounts/login.html` → Form template
- `static/css/accounts/login.css` → Styling

**Code Flow:**

```
1. User visits /accounts/login/?role=student
   ↓
2. login_view() checks if already authenticated
   - If yes: redirect_by_role() sends to respective dashboard
   - If no: renders login form with role tabs
   ↓
3. User enters credentials based on role:
   
   ADMIN LOGIN:
   - Input: username (accepts "219" or "user-219")
   - Input: password "8120" (hardcoded)
   - Code checks: if username_input == 'user-219' and password == '8120'
   - Creates admin user if not exists (set as is_staff & is_superuser)
   - Redirects to /admin-panel/dashboard/
   
   STUDENT LOGIN:
   - Input: enrollment number (from UserProfile.enrollment_number)
   - Input: password (from User.password)
   - Code: UserProfile.objects.get(enrollment_number=enrollment)
   - Calls user.check_password(password) for verification
   - Redirects to /student/dashboard/
   
   ORGANIZER LOGIN:
   - Input: Gmail (from User.email)
   - Input: password
   - Code: User.objects.get(email=email)
   - Checks : profile.role == 'organizer' and user.check_password(password)
   - Redirects to /organizer/dashboard/
   
4. redirect_by_role() function determines dashboard based on role
```

**Templates & Styling:**
- `login.html` has role tabs (🔑 Admin, 🎯 Organizer, 🎓 Student)
- Role tabs switch forms without page reload (GET parameter in URL)
- `login.css` styles the gradient background and form box

---

### 1.3 Registration Flow

**Route:** `GET/POST /accounts/register/?role={student|organizer}`

**Files Involved:**
- `accounts/views.py` → `register_view()` function
- `templates/accounts/register.html` → Form template
- `static/css/accounts/register.css` → Styling

**Code Flow:**

```
1. User selects role and visits /accounts/register/?role=student
   ↓
2. register_view() renders registration form
   ↓
3. User fills form:
   - Name (first_name in User model)
   - Email (must be unique)
   - Department, Branch
   - Password x2 (confirmation)
   - STUDENT ONLY: Enrollment Number (unique)
   ↓
4. Validation checks:
   - Passwords match?
   - Email already registered?
   - Enrollment number already exists? (for students)
   ↓
5. If valid:
   - Create User object with email as username
   - Create UserProfile with role='student' or 'organizer'
   - Store enrollment_number/department/branch
   ↓
6. Redirect to login page: /accounts/login/?role={role}
```

**Key Code:**
```python
user = User.objects.create_user(
    username=email,
    email=email,
    password=password,
    first_name=name
)
UserProfile.objects.create(
    user=user,
    role='student',  # or 'organizer'
    enrollment_number=enrollment,
    department=department
)
```

---

### 1.4 Logout & Role-based Redirects

**Route:** `GET /accounts/logout/`

**Code Flow:**
```
logout_view() → django.contrib.auth.logout(request)
             → Destroy session
             → Redirect to home page /
```

**redirect_by_role() function:**
```python
def redirect_by_role(user):
    if user.is_superuser OR user.profile.role == 'admin':
        return /admin-panel/dashboard/
    elif user.profile.role == 'organizer':
        return /organizer/dashboard/
    else:
        return /student/dashboard/
```

---

---

## 2️⃣ EVENT CREATION & MANAGEMENT FLOW

### 2.1 Event Data Model
**Files:** `organizer_app/models.py`

```python
class Event(models.Model):
    organizer = models.ForeignKey(User)  # Creator
    title, description, category  # Basic info
    department, venue, event_date, event_time  # Location & time
    registration_deadline, max_capacity  # Capacity
    team_event, min_team_size, max_team_size  # Team settings
    poster = models.ImageField(upload_to='event_posters/')
    status = ['pending', 'active', 'correction', 'rejected', 'completed', 'cancelled']
    admin_note = models.TextField()  # Corrections/rejection reason
```

**Status Lifecycle:**
```
pending → admin reviews → active/correction/rejected
                ↓
           (if correction) → organizer edits → pending again
           (if active) → students register → completed
```

---

### 2.2 Event Creation Flow

**Route:** `GET/POST /organizer/create-event/`

**Files Involved:**
- `organizer_app/views.py` → `create_event()` function
- `templates/organizer/create_event.html` → Form template
- `organizer_app/models.py` → Event model

**Decorator Protection:**
```python
@organizer_required  # Checks: user authenticated + role == 'organizer'
def create_event(request):
```

**Code Flow:**

```
1. Organizer clicks "Create Event" button
   ↓
2. Renders create_event.html form with fields:
   - Title, Description, Category
   - Department, Venue
   - Event Date, Time, Registration Deadline
   - Max Capacity, Team Settings
   - Upload Poster Image
   ↓
3. Upon form submission (POST):
   - Collect all form data
   - Create Event object with status='pending'
   - Save poster image to media/event_posters/
   ↓
4. Event saved to database
   ↓
5. Message: "Event submitted for admin approval!"
   ↓
6. Redirect to /organizer/dashboard/
   
   (Event is NOT visible to students yet - waiting for admin approval)
```

**Key Code:**
```python
event = Event(
    organizer=request.user,
    title=request.POST.get('title'),
    category=request.POST.get('category'),
    status='pending',  # Not active until admin approves
)
event.poster = request.FILES['poster']
event.save()
```

---

### 2.3 Event Approval Flow (Admin Review)

**Route:** `GET/POST /admin-panel/review-event/<event_id>/`

**Files Involved:**
- `admin_panel/views.py` → `review_event()` function
- `templates/admin_panel/review_event.html` → Review form
- `organizer_app/models.py` → Event model

**Decorator Protection:**
```python
@admin_required  # Checks: user authenticated + (role == 'admin' OR is_superuser)
def review_event(request, pk):
```

**Code Flow:**

```
1. Admin visits Events > Pending Events page
   - Shows all events with status='pending'
   ↓
2. Admin clicks on event to review
   - Shows event details, description, poster
   - Shows registrations (initially empty)
   ↓
3. Admin chooses action:
   
   A) APPROVE EVENT:
      - Click "Approve" button
      - event.status = 'active'
      - event.admin_note = ''
      - Save & redirect
      - Message: "Event approved and is now LIVE!"
      → NOW STUDENTS CAN SEE & REGISTER FOR THIS EVENT
   
   B) REQUEST CORRECTION:
      - Enter note explaining what needs to be fixed
      - event.status = 'correction'
      - event.admin_note = note
      - Save & redirect
      → Organizer gets notification to edit event
      → Organizer submits again for re-review
   
   C) REJECT EVENT:
      - Enter rejection reason
      - event.status = 'rejected'
      - event.admin_note = reason
      - Save & redirect
      → Event is deleted/hidden from system
   
   D) MARK COMPLETED:
      - After event happens
      - event.status = 'completed'
      → No more registrations allowed
      → Certificates can be issued
```

**Key Code:**
```python
if action == 'approve':
    event.status = 'active'
    event.save()
    messages.success(request, 'Event approved and is now LIVE!')

elif action == 'correction':
    event.status = 'correction'
    event.admin_note = note
    event.save()
    # Organizer can now edit
```

---

### 2.4 Event Editing Flow (After Correction Request)

**Route:** `GET/POST /organizer/edit-event/<event_id>/`

**Files Involved:**
- `organizer_app/views.py` → `edit_event()` function
- `templates/organizer/edit_event.html` → Edit form

**Restrictions:**
```python
# Cannot edit if event is already active (to prevent tampering)
if event.status == 'active':
    messages.error(request, 'Cannot edit an active event.')
    return redirect(...)

# CAN edit if:
# - status='pending' (not yet reviewed)
# - status='correction' (admin requested changes)
```

**Code Flow:**

```
1. Organizer visits dashboard
   - Sees all their events
   - Events with status='correction' show admin_note
   ↓
2. Organizer clicks "Edit" on correction event
   - Form pre-filled with current event data
   ↓
3. Organizer makes changes and submits
   - All fields updated
   - status automatically changes back to 'pending'
   ↓
4. Event resubmitted to admin review
   - Returns to pending_events list
   - Admin reviews again
```

---

---

## 3️⃣ STUDENT REGISTRATION & EVENT DISCOVERY

### 3.1 Discover Events Flow

**Route:** `GET /student/discover/?category=technical&search=python`

**Files Involved:**
- `student_app/views.py` → `discover_events()` function
- `templates/student/discover.html` → Events listing
- `student_app/models.py` → Registration model

**Decorator Protection:**
```python
@student_required  # Checks: user authenticated + role == 'student'
def discover_events(request):
```

**Code Flow:**

```
1. Student visits /student/discover/
   ↓
2. discover_events() fetches ALL ACTIVE events:
   - Filter: Event.objects.filter(status='active')
   - Sort by event_date (nearest first)
   ↓
3. Apply optional filters:
   - Category filter: ?category=technical
     → events.filter(category=category)
   
   - Search filter: ?search=coding
     → events.filter(title__icontains='coding') 
       OR events.filter(description__icontains='coding')
   ↓
4. Check which events student already registered for:
   - registered_ids = Registration.objects.filter(
       student=request.user, status='confirmed'
     ).values_list('event_id')
   ↓
5. Render template with:
   - All filtered active events
   - List of event_ids already registered
   - Mark duplicate registrations as "Already Registered"
```

**Key Code:**
```python
events = Event.objects.filter(status='active').order_by('event_date')

if category:
    events = events.filter(category=category)

if search:
    events = events.filter(title__icontains=search) | \
             events.filter(description__icontains=search)

registered_ids = Registration.objects
    .filter(student=request.user, status='confirmed')
    .values_list('event_id', flat=True)
```

**Template Display (discover.html):**
- Shows event cards with:
  - Event title, date, time, venue
  - Category badge (🔵 Technical, 🎨 Cultural, etc.)
  - Current registrations / Max capacity
  - "Register" button (disabled if already registered)

---

### 3.2 Event Registration Flow

**Route:** `POST /student/register-event/<event_id>/`

**Files Involved:**
- `student_app/views.py` → `register_event()` function
- `student_app/models.py` → Registration model
- `templates/student/register_event.html` → Registration form

**Code Flow:**

```
1. Student clicks "Register" on event card
   ↓
2. register_event() performs checks:
   
   Check 1: Already registered?
   - if Registration.objects.filter(
       student=request.user, event=event
     ).exists():
     → messages.info('Already registered!')
     → redirect to dashboard
   
   Check 2: Event full?
   - current_registrations = event.registered_count()
   - if current_registrations >= event.max_capacity:
     → messages.error('Event is full.')
     → redirect to discover page
   
   Check 3: Is event a TEAM event?
   - if event.team_event == True:
     → Show form to enter:
       - Team name
       - Team members (comma-separated)
       - Validate min_team_size <= members <= max_team_size
   
   Check 4: Is event a SOLO event?
   - if event.team_event == False:
     → Just confirm registration
   ↓
3. Create Registration object:
   - Registration.objects.create(
       student=request.user,
       event=event,
       team_name = form_input or '',
       team_members = form_input or '',
       status='confirmed',
       # ticket_number auto-generated in save()
     )
   ↓
4. Auto-generate Ticket:
   - Random 6-digit ticket_number
   - Used for QR code at check-in
   ↓
5. Success message: "Registered successfully!"
   ↓
6. Redirect to /student/my-events/
```

**Registration Model:**
```python
class Registration(models.Model):
    student = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    team_name, team_members  # For team events
    status = ['confirmed', 'cancelled', 'waitlist']
    ticket_number  # 6-digit unique number
    checked_in = False  # Set to True when organizer checks in
    checked_in_at = None  # Timestamp of check-in
    
    # Unique constraint: same student can't register for same event twice
    class Meta:
        unique_together = ('student', 'event')
```

---

### 3.3 Student Dashboard - My Events

**Route:** `GET /student/dashboard/`

**Files Involved:**
- `student_app/views.py` → `dashboard()` function
- `templates/student/dashboard.html` → Dashboard view

**Code Flow:**

```
1. Student visits /student/dashboard/
   ↓
2. dashboard() fetches student's data:
   
   A) All Registrations:
      - registrations = Registration.objects.filter(
          student=request.user, status='confirmed'
        )
   
   B) Split into Upcoming vs Past:
      - upcoming = registrations.filter(
          event__event_date >= today
        )
      - past = registrations.filter(
          event__event_date < today
        )
   
   C) Certificates earned:
      - certificates = Certificate.objects.filter(
          student=request.user
        )
   
   D) Recent announcements:
      - announcements = Announcement.objects.all()
        .order_by('-created_at')[:5]
   
3. Render dashboard with:
   - Upcomng events count
   - Past events
   - Certificates count
   - Event cards with:
     - Title, date, venue
     - "View Ticket" button
     - "Give Feedback" button (for past events)
     - "Download Certificate" button (if certificate issued)
```

---

### 3.4 Event Ticket - QR Code Check-in

**Route:** `GET /student/ticket/<registration_id>/`

**Files Involved:**
- `student_app/views.py` → `view_ticket()` function
- `templates/student/ticket.html` → Ticket display

**Code Flow:**

```
1. Student clicks "View Ticket" from My Events
   ↓
2. view_ticket() generates:
   - Ticket number (from Registration.ticket_number)
   - QR code embedding: registration_id + ticket_number
   - Event details, student name, date
   ↓
3. Display ticket with:
   - Student name
   - Event name & date
   - QR code image
   - Ticket number (6 digits)
   ↓
4. At event venue:
   - Organizer scans QR code
   - Or manually enters ticket number
   - Redirects to check-in page
```

---

---

## 4️⃣ ORGANIZER ATTENDANCE & CHECK-IN

### 4.1 Organizer Dashboard

**Route:** `GET /organizer/dashboard/`

**Files Involved:**
- `organizer_app/views.py` → `dashboard()` function
- `templates/organizer/dashboard.html` → Dashboard

**Code Flow:**

```
1. Organizer visits /organizer/dashboard/
   ↓
2. dashboard() collects statistics:
   
   - total_events = Event.objects.filter(organizer=user).count()
   - active_events = Event.objects.filter(organizer=user, status='active').count()
   - pending_events = Event.objects.filter(organizer=user, status='pending').count()
   
   - total_registrations = Registration.objects.filter(
       event__organizer=user, status='confirmed'
     ).count()
   
   - Recent events (last 5 created)
   - Category breakdown (registrations per category)
   
3. Render dashboard with:
   - Key stats cards
   - Recent events list
   - Announcements sent
```

---

### 4.2 Event Attendance - Live Check-in

**Route:** `GET /organizer/analytics/<event_id>/`

**Files Involved:**
- `organizer_app/views.py` → `event_analytics()` function
- `templates/organizer/analytics.html` → Attendance tracker

**Code Flow:**

```
1. Organizer opens Event Analytics page
   ↓
2. event_analytics() fetches:
   - All registrations for this event
   - Total registered, checked-in, no-show counts
   ↓
3. Display table with:
   - Student name
   - Team name (if team event)
   - Registration time
   - Status: ✓ Checked In / ✗ Not Checked In
   - Check-In Time
   ↓
4. Organizer scans QR code or enters ticket number:
   - Calls mark_attendance() function
   ↓
5. mark_attendance() code:
   - GET registration by ticket_number
   - Set checked_in = True
   - Set checked_in_at = current datetime
   - Save registration
   - Update attendance table in real-time
```

**Key Code:**
```python
def mark_attendance(request, event_id, ticket_number):
    registration = Registration.objects.get(
        event_id=event_id,
        ticket_number=ticket_number
    )
    registration.checked_in = True
    registration.checked_in_at = timezone.now()
    registration.save()
```

---

---

## 5️⃣ ADMIN ANALYTICS & USER MANAGEMENT

### 5.1 Admin Dashboard

**Route:** `GET /admin-panel/dashboard/`

**Files Involved:**
- `admin_panel/views.py` → `dashboard()` function
- `templates/admin_panel/dashboard.html` → Analytics

**Code Flow:**

```
1. Admin visits /admin-panel/dashboard/
   ↓
2. dashboard() collects platform statistics:
   
   - total_events = Event.objects.count()
   - pending_events = Event.objects.filter(status='pending').count()
   - active_events = Event.objects.filter(status='active').count()
   - total_students = UserProfile.objects.filter(role='student').count()
   - total_organizers = UserProfile.objects.filter(role='organizer').count()
   - total_registrations = Registration.objects.filter(status='confirmed').count()
   
   - recent_pending = Event.objects.filter(status='pending')
     .order_by('-created_at')[:5]
   
3. Render dashboard with:
   - Key metric cards
   - Chart of pending events
   - Recent events list
   - Quick action buttons
```

---

### 5.2 Pending Events List

**Route:** `GET /admin-panel/pending-events/`

**Files Involved:**
- `admin_panel/views.py` → `pending_events()` function
- `templates/admin_panel/pending_events.html` → List

**Code Flow:**

```
1. Admin clicks "Pending Events" in sidebar
   ↓
2. pending_events() fetches:
   - events = Event.objects.filter(status='pending')
     .order_by('-created_at')
     .select_related('organizer')
   ↓
3. Display list with:
   - Event title (clickable to review)
   - Organizer name
   - Category
   - Created date
   - Current registrations
   ↓
4. Admin clicks event to review (go to review_event flow)
```

---

### 5.3 All Events Management

**Route:** `GET /admin-panel/all-events/?status=active`

**Files Involved:**
- `admin_panel/views.py` → `all_events()` function
- `templates/admin_panel/all_events.html` → Filtered list

**Code Flow:**

```
1. Admin visits All Events page
   ↓
2. Optional filter by status:
   - ?status=active → Show only active events
   - ?status=completed → Show completed events
   - ?status=pending → Show pending
   - No parameter → Show ALL events
   ↓
3. all_events() code:
   - events = Event.objects.all().order_by('-created_at')
   - if status_filter:
       events = events.filter(status=status_filter)
   ↓
4. Display table with:
   - Event name, organizer, category
   - Current status badge
   - Registrations count
   - Action links (Review, Edit, Delete)
```

---

### 5.4 User Management

**Route:** `GET /admin-panel/manage-users/`

**Files Involved:**
- `admin_panel/views.py` → `manage_users()` function
- `templates/admin_panel/manage_users.html` → User list

**Code Flow:**

```
1. Admin visits Manage Users page
   ↓
2. manage_users() fetches:
   - students = UserProfile.objects.filter(role='student')
   - organizers = UserProfile.objects.filter(role='organizer')
   - admins = UserProfile.objects.filter(role='admin')
   ↓
3. Display table with:
   - User name, email, role, enrollment/department
   - Account status
   - Action buttons (Activate, Deactivate, Delete)
   ↓
4. Actions available:
   
   A) ACTIVATE USER:
      - user.is_active = True
      - Save & refresh
   
   B) DEACTIVATE USER:
      - user.is_active = False
      - User can no longer login
   
   C) DELETE USER:
      - user.delete()
      - Also deletes related UserProfile, events, registrations
```

---

---

## 6️⃣ CERTIFICATES & VERIFICATION

### 6.1 Certificate Model

**Files:** `student_app/models.py`

```python
class Certificate(models.Model):
    CERT_TYPE_CHOICES = [
        ('participation', 'Participation'),
        ('winner_1', '1st Place'),
        ('winner_2', '2nd Place'),
        ('winner_3', '3rd Place'),
        ('organizer', 'Organizer'),
    ]
    
    student = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    cert_type = models.CharField(choices=CERT_TYPE_CHOICES)
    issued_at = models.DateTimeField(auto_now_add=True)
    cert_number = models.CharField(unique=True)  # CERT-XXXXXXXX
```

---

### 6.2 Certificate Issuance Flow (Organizer)

**Route:** `POST /organizer/issue-certificate/<event_id>/`

**Files Involved:**
- `organizer_app/views.py` → `issue_certificate()` function
- `templates/organizer/issue_certificate.html` → Forms

**Code Flow:**

```
1. Event completed, organizer goes to event dashboard
   ↓
2. Clicks "Issue Certificates" button
   ↓
3. issue_certificate() displays form:
   - Dropdown: Choose certificate type
     - Participation (for all attendees)
     - 1st Place (for winners)
     - 2nd Place
     - 3rd Place
   
   - Search field: Select students who checked in
     - Only students with checked_in=True shown
   ↓
4. Organizer selects students and certificate type
   ↓
5. Upon submit, for each selected student:
   - Certificate.objects.create(
       student=student,
       event=event,
       cert_type=cert_type,
       # cert_number auto-generated in save()
     )
   ↓
6. Auto-generate certificate number:
   - Format: CERT-{12345678} (random alphanumeric)
   ↓
7. Success message + redirect to dashboard
```

---

### 6.3 Student Downloads Certificates

**Route:** `GET /student/certificates/`

**Files Involved:**
- `student_app/views.py` → `certificates()` function
- `templates/student/certificates.html` → Certificate list

**Code Flow:**

```
1. Student visits My Certificates page
   ↓
2. certificates() fetches:
   - certs = Certificate.objects.filter(student=request.user)
     .select_related('event')
   ↓
3. Display certificate cards with:
   - Event name, date
   - Certificate type (Participation / 1st Place)
   - Issue date
   - Certificate number
   - "Download PDF" button
   ↓
4. Download flow:
   - User clicks "Download PDF"
   - generatePDF() function creates certificate image
   - File downloaded as: Event_Name_Certificate.pdf
```

---

---

## 7️⃣ FEEDBACK & RATINGS

### 7.1 Feedback Model

**Files:** `student_app/models.py`

```python
class EventFeedback(models.Model):
    student = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    rating = models.IntegerField(choices=[(1,1), (2,2), ... (5,5)])
    content_quality = models.IntegerField(default=3)  # 1-5
    organization = models.IntegerField(default=3)    # 1-5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'event')  # One feedback per student per event
```

---

### 7.2 Submit Feedback Flow

**Route:** `POST /student/feedback/<event_id>/`

**Files Involved:**
- `student_app/views.py` → `submit_feedback()` function
- `templates/student/feedback.html` → Feedback form

**Code Flow:**

```
1. Student views past event in My Events
   ↓
2. Clicks "Give Feedback" button
   - Only appears for PAST events (event_date < today)
   ↓
3. submit_feedback() checks:
   - Did student register for this event?
     if no → error, redirect
   
   - Did student attend (checked_in=True)?
     if no → warning, but still allow feedback
   
   - Already submitted feedback?
     if yes → show existing feedback in edit mode
   ↓
4. Render feedback form with fields:
   - Overall Rating: ⭐⭐⭐⭐⭐ (1-5 stars)
   - Content Quality: 1-5 scale
   - Organization: 1-5 scale
   - Comments: Text area for general feedback
   ↓
5. Upon form submit:
   - EventFeedback.objects.create(
       student=request.user,
       event=event,
       rating=form['rating'],
       content_quality=form['content_quality'],
       organization=form['organization'],
       comment=form['comment']
     )
   ↓
6. Success message: "Feedback submitted!"
   ↓
7. Student can later edit feedback if submitted again
```

---

### 7.3 View Feedback Summary (Organizer Analytics)

**Route:** `GET /organizer/analytics/<event_id>/`

**Files Involved:**
- `organizer_app/views.py` → Analytics view
- `templates/organizer/analytics.html` → Analytics dashboard

**Code Flow:**

```
1. Organizer visits event analytics
   ↓
2. Analytics view calculates:
   
   - avg_rating = Feedback.objects.filter(event=event)
     .aggregate(Avg('rating'))['rating__avg']
   
   - feedback_count = Feedback.objects.filter(event=event).count()
   
   - avg_content_quality = Aggregate avg of content_quality
   
   - avg_organization = Aggregate avg of organization
   
3. Display:
   - Overall rating: 4.5/5 (based on student ratings)
   - Average scores for content, organization
   - Recent comments list
   - Feedback visualization charts
```

---

---

## 📊 DATABASE RELATIONSHIPS DIAGRAM

```
User (Django)
  ├─ 1:1 → UserProfile (role: student/organizer/admin)
  │
  ├─ 1:Many → Event (organizer)
  │
  ├─ 1:Many → Registration (student)
  │             ├─ Many:1 → Event
  │             ├─ checked_in: Boolean
  │             └─ ticket_number: String (for QR)
  │
  ├─ 1:Many → Certificate (student)
  │             └─ Many:1 → Event
  │
  ├─ 1:Many → EventFeedback (student)
  │             └─ Many:1 → Event
  │
  └─ 1:Many → Announcement (organizer/admin)


Event
  ├─ status: pending → active/correction/rejected → completed
  ├─ organizer: ForeignKey(User)
  ├─ 1:Many → Registration (students registered)
  ├─ 1:Many → Certificate (issued certs)
  ├─ 1:Many → EventFeedback (student ratings)
  └─ 1:Many → EventCoordinator (additional coordinators)
```

---

---

## 🔐 AUTHORIZATION DECORATORS

All views use custom decorators to ensure only authorized users can access:

**Files:** `accounts/views.py`, `organizer_app/views.py`, `student_app/views.py`, `admin_panel/views.py`

```python
# For Admin Pages
@admin_required
def dashboard(request):
    # Checks:
    # 1. User is authenticated
    # 2. User.profile.role == 'admin' OR user.is_superuser
    # 3. If fails → redirect to home with error message

# For Organizer Pages
@organizer_required
def create_event(request):
    # Checks:
    # 1. User is authenticated
    # 2. User.profile.role == 'organizer'
    # 3. If fails → redirect to login page with role=organizer

# For Student Pages
@student_required
def discover_events(request):
    # Checks:
    # 1. User is authenticated
    # 2. User.profile.role == 'student'
    # 3. If fails → redirect to login page with role=student
```

---

---

## 🎨 FRONTEND ARCHITECTURE

**CSS Organization:**
- `static/css/base.css` - Global styles, variables, layout system
  - CSS variables: --purple, --teal, --red, etc.
  - Component styles: .btn, .card, .badge, .form-control
  - Layout: Sidebar + Main content grid
  - Responsive utilities

- `static/css/accounts/login.css` - Login form styling
- `static/css/accounts/register.css` - Registration form styling
- `static/css/landing/home.css` - Landing page styles

**Template Inheritance:**
```
base.html (master template with sidebar, topbar)
  ├─ landing/home.html (public landing page)
  ├─ accounts/login.html (login form)
  ├─ accounts/register.html (registration form)
  ├─ admin_panel/
  │   ├─ dashboard.html
  │   ├─ pending_events.html
  │   ├─ all_events.html
  │   ├─ review_event.html
  │   └─ manage_users.html
  ├─ organizer/
  │   ├─ dashboard.html
  │   ├─ create_event.html
  │   ├─ edit_event.html
  │   ├─ analytics.html
  │   └─ announcement.html
  └─ student/
      ├─ dashboard.html
      ├─ discover.html
      ├─ register_event.html
      ├─ ticket.html
      ├─ certificates.html
      └─ feedback.html
```
