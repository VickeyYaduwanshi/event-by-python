# 🎓 Campus Events Hub — Quick Reference (100 Lines)

## Project Overview
Django-based college event management system with 3 roles: Student, Organizer, Admin. Students register for events, organizers create & manage events, admin approves & controls platform.

---

## Folder Responsibilities

| Folder | Purpose |
|--------|---------|
| **accounts/** | Login/Register/UserProfile (models.py has User + UserProfile with role field) |
| **organizer_app/** | Event CRUD, announcements, attendance tracking (Event model, views.py functions) |
| **student_app/** | Registration, tickets, certificates, feedback (Registration, Certificate, EventFeedback models) |
| **admin_panel/** | Event approval/rejection, user management, analytics (no models, uses existing Event/User) |
| **landing/** | Home page (featured events + stats) |
| **static/css/** | 4 CSS files (base.css, login.css, register.css, home.css) |

---

## Main Flows (Code Path)

### User Registration
- **URL**: `POST /accounts/register/`
- **Function**: `accounts.views.register_view()` (Line 100-146)
- **Logic**: Form validate → `User.objects.create_user()` → `UserProfile.objects.create(role='student'/'organizer')`
- **DB**: User table + UserProfile table

### User Login
- **URL**: `GET/POST /accounts/login/?role=student`
- **Function**: `accounts.views.login_view()` (Line 10-78)
- **Logic**: 
  - Student: `UserProfile.objects.get(enrollment_number=X)` → `user.check_password()`
  - Organizer: `User.objects.get(email=X)` → `user.check_password()`
  - Admin: Hardcoded (user-219 / 8120)
- **Result**: Django session create + redirect_by_role()

### Event Creation
- **URL**: `POST /organizer/create/`
- **Function**: `organizer_app.views.create_event()` (Line 39-74)
- **Logic**: `Event.objects.create(organizer=request.user, status='pending')` → Image upload to `media/event_posters/`
- **Status**: pending (waiting admin approval)

### Event Approval
- **URL**: `POST /admin-panel/events/<id>/review/`
- **Function**: `admin_panel.views.review_event()` (Line 58-103)
- **Actions**: approve (status='active'), correction (status='correction'), reject, complete
- **Result**: Active events visible to students in Discover page

### Event Registration
- **URL**: `POST /student/register/<event_id>/`
- **Function**: `student_app.views.register_event()` (Line 48-77)
- **Logic**: Check if already registered + event full? → `Registration.objects.create(status='confirmed', ticket_number=auto_generate())`
- **DB**: Registration table

### Attendance Check-in
- **URL**: `POST /organizer/checkin/<registration_id>/`
- **Function**: `organizer_app.views.checkin_student()` (Line 125-133)
- **Logic**: `reg.checked_in=True`, `reg.checked_in_at=timezone.now()`, `reg.save()`
- **DB Update**: Registration table

### Certificate Issue
- **URL**: `POST /organizer/certificate/<registration_id>/`
- **Function**: `organizer_app.views.issue_certificate()` (Line 178-188)
- **Logic**: `Certificate.objects.get_or_create(cert_type='participation'/'winner_1'/etc)`
- **DB**: Certificate table

### Student Feedback
- **URL**: `POST /student/feedback/<event_id>/`
- **Function**: `student_app.views.submit_feedback()` (Line 116-145)
- **Logic**: Check registration exists → `EventFeedback.objects.get_or_create(rating, content_quality, organization, comment)`
- **DB**: EventFeedback table (unique_together: student+event)

---

## Database Tables (Quick)

```
User: id, username, email, password(hashed), is_active, is_superuser
UserProfile: id, user_id(FK), role, enrollment_number(unique), department, branch
Event: id, organizer_id(FK), title, category, status(7 choices), event_date, max_capacity, poster
Registration: id, student_id(FK), event_id(FK), status, ticket_number(6-digit unique), checked_in, checked_in_at
Certificate: id, student_id(FK), event_id(FK), cert_type, cert_number(CERT-8digits)
EventFeedback: id, student_id(FK), event_id(FK), rating(1-5), content_quality, organization, comment
Announcement: id, organizer_id(FK), event_id(FK), subject, message, priority
```

---

## Key Functions (38 Total - Main Ones Listed)

**Accounts**: login_view(), register_view(), logout_view(), redirect_by_role()

**Organizer**: create_event(), edit_event(), event_detail(), checkin_student(), send_announcement(), issue_certificate(), analytics()

**Student**: dashboard(), discover_events(), register_event(), my_ticket(), my_events(), certificates(), cancel_registration(), submit_feedback()

**Admin**: dashboard(), pending_events(), all_events(), review_event(), manage_users(), toggle_user(), admin_analytics(), issue_cert_admin()

**Landing**: home()

---

## Authorization Decorators

```python
@admin_required    # Checks: is_authenticated + (role=='admin' OR is_superuser)
@organizer_required # Checks: is_authenticated + role=='organizer'
@student_required   # Checks: is_authenticated + role=='student'
```

---

## Important: Event Status Lifecycle

```
pending → (admin approves) → active
       → (admin requests correction) → correction
       → (admin rejects) → rejected
       
active → (organizer/admin marks) → completed
      → (cancellation) → cancelled
```

---

## URL Routing (28 Routes)

**Auth**: /accounts/login/, /accounts/register/, /accounts/logout/

**Student**: /student/dashboard/, /student/discover/, /student/register/<id>/, /student/ticket/<id>/, /student/my-events/, /student/certificates/, /student/feedback/<id>/, /student/cancel/<id>/

**Organizer**: /organizer/dashboard/, /organizer/create/, /organizer/edit/<id>/, /organizer/event/<id>/, /organizer/checkin/<id>/, /organizer/announce/, /organizer/certificate/<id>/, /organizer/analytics/

**Admin**: /admin-panel/dashboard/, /admin-panel/pending/, /admin-panel/events/, /admin-panel/events/<id>/review/, /admin-panel/users/, /admin-panel/users/<id>/toggle/, /admin-panel/analytics/, /admin-panel/cert/<id>/issue/

**Home**: / (landing page)

---

## Files Organization

```
college_events/
├── accounts/ (authentication)
├── organizer_app/ (events)
├── student_app/ (registrations)
├── admin_panel/ (approvals)
├── landing/ (home)
├── templates/ (HTML)
├── static/css/ (4 CSS files)
├── media/ (uploads)
├── db.sqlite3 (database)
└── manage.py
```

---

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_initial_data
python manage.py runserver
# http://127.0.0.1:8000/
```

**Login Credentials:**
- Admin: user-219 / 8120
- Student: enrollment_number / password
- Organizer: email / password

---

## Key Concepts

1. **Role-based Access**: UserProfile.role determines dashboard + permissions
2. **Event Workflow**: pending→active→completed (3-step approval process)
3. **Registrations**: Student→Event mapping with automatic ticket generation
4. **Attendance**: QR-based check-in (6-digit ticket number)
5. **Certificates**: Auto-generated certificate numbers (CERT-XXXXXXXX)
6. **Analytics**: Dashboard views with aggregated data (events by category/status, top events, attendance rates)
7. **Decorators**: Every sensitive view protected by role-check decorator
