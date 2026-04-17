# Role-Based Access Control (RBAC) - College Events Project

## Overview
This Django project implements a **simple three-tier RBAC system** where every user has one of three roles: **Admin**, **Organizer**, or **Student**. Access control is enforced at three levels: authentication, role decorators, and resource ownership.

---

## 1. Role System Architecture

### User Model Structure
```python
# accounts/models.py
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    enrollment_number = models.CharField(max_length=20, unique=True, null=True)
    branch = models.CharField(max_length=50, null=True, blank=True)
    
    def is_student(self):
        return self.role == 'student'
    def is_organizer(self):
        return self.role == 'organizer'
    def is_admin(self):
        return self.role == 'admin'
```

Each Django `User` gets a linked `UserProfile` with a role assigned at registration. Roles are immutable—once assigned, they don't change.

---

## 2. Authentication & Role-Based Redirects

### Login Workflow

The login process differentiates credentials by role:

```python
# accounts/views.py - Login for each role type
def login_view(request):
    role = request.GET.get('role', 'student')  # student, organizer, or admin
    
    if request.method == 'POST':
        if role == 'admin':
            username = '219'  # Hardcoded admin credentials
            password = '8120'
        elif role == 'organizer':
            username = request.POST['email']
            password = request.POST['password']
        else:  # student
            username = request.POST['enrollment_number']
            password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user and user.profile.role == role:
            login(request, user)
            return redirect_by_role(user)  # Redirect to role dashboard
        else:
            return error_response("Invalid credentials or role mismatch")
```

### Role-Based Dashboard Redirect
```python
def redirect_by_role(user):
    profile = user.profile
    if profile.role == 'admin':
        return redirect('/admin-panel/dashboard/')
    elif profile.role == 'organizer':
        return redirect('/organizer/dashboard/')
    else:
        return redirect('/student/dashboard/')
```

---

## 3. Access Control: Decorator Pattern

Every view in each app is protected by a role-checking decorator. If a user's role doesn't match, they're redirected.

### Admin Decorator
```python
# admin_panel/views.py
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

# Usage in views
@admin_required
def admin_dashboard(request):
    # Only accessible to admin users
    pending_events = Event.objects.filter(status='pending')
    return render(request, 'admin/dashboard.html', {'events': pending_events})
```

### Organizer Decorator
```python
# organizer_app/views.py
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
def create_event(request):
    # Only accessible to organizer users
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('event_detail', pk=event.pk)
    return render(request, 'organizer/create_event.html', {'form': EventForm()})
```

### Student Decorator
```python
# student_app/views.py
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
def student_dashboard(request):
    # Only accessible to student users
    my_events = Registration.objects.filter(student=request.user)
    return render(request, 'student/dashboard.html', {'registrations': my_events})
```

---

## 4. Resource-Level Access Control (Ownership Checks)

Beyond role decorators, the system verifies **resource ownership** to prevent users from accessing other people's data.

### Organizer Event Ownership
```python
# organizer_app/views.py
@organizer_required
def edit_event(request, pk):
    # Ensure organizer only edits their own events
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', pk=event.pk)
    
    form = EventForm(instance=event)
    return render(request, 'organizer/edit_event.html', {'form': form, 'event': event})
```

### Student Registration Ownership
```python
# student_app/views.py
@student_required
def feedback(request, pk):
    # Ensure student only submits feedback for their own registrations
    reg = get_object_or_404(Registration, pk=pk, student=request.user)
    
    if request.method == 'POST':
        reg.feedback = request.POST['feedback']
        reg.save()
        messages.success(request, 'Feedback submitted!')
        return redirect('my_events')
    
    return render(request, 'student/feedback.html', {'registration': reg})
```

---

## 5. Role Permissions Matrix

| Feature | Admin | Organizer | Student |
|---------|:-----:|:---------:|:-------:|
| **Approve/Reject Events** | ✓ | - | - |
| **View All Users** | ✓ | - | - |
| **Create Events** | - | ✓ | - |
| **Edit Own Events** | - | ✓ | - |
| **Issue Certificates** | ✓ | ✓ | - |
| **Manage Check-ins** | - | ✓ | - |
| **Register for Events** | - | - | ✓ |
| **View Own Registrations** | - | - | ✓ |
| **Submit Feedback** | - | - | ✓ |
| **View Analytics** | ✓ | ✓ | - |

---

## 6. URL Routing by Role

```python
# college_events/urls.py
urlpatterns = [
    path('', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin-panel/', include('admin_panel.urls')),     # Admin only
    path('organizer/', include('organizer_app.urls')),     # Organizer only
    path('student/', include('student_app.urls')),         # Student only
]
```

Each app's URLs are isolated and protected by decorators, creating separate namespaces for different roles.

---

## 7. How the Flow Works (End-to-End)

### Step 1: Registration
```
User fills form → Role selected (student/organizer/admin) 
→ UserProfile created with role='student'/'organizer'/'admin'
```

### Step 2: Login
```
User enters credentials for their role type
→ Server verifies role matches
→ Session created
→ Redirected to role-specific dashboard
```

### Step 3: Access Request
```
User requests view (e.g., /organizer/create-event/)
→ @organizer_required decorator checks role
→ If role ≠ 'organizer' → Redirect to home
→ If role == 'organizer' → Process request
→ Resource ownership verified (if applicable)
→ Response rendered with role-specific data
```

---

## 8. Key Characteristics

### ✅ Strengths
- **Simple & lightweight**: No external RBAC packages needed
- **Clear separation**: Each role has isolated app and URLs
- **Ownership verification**: Prevents cross-user data access
- **Easy to understand**: Decorator pattern is intuitive

### ⚠️ Limitations
- **No fine-grained permissions**: Can't restrict specific actions within a role (e.g., "organizer can only delete their own events")
- **Hardcoded admin credentials**: Security risk—should use environment variables
- **No audit logging**: No record of who accessed what and when
- **Frontend leakage**: Role-based content in templates isn't protected from inspection
- **Single role per user**: Users can't have multiple roles

---

## 9. Security Recommendations

```python
# BEFORE (Security Risk)
if role == 'admin':
    username = '219'
    password = '8120'

# AFTER (Recommended)
import os
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
# Store in .env file, never in code
```

---

## Summary

This project uses **role-based access control** to segregate users into **three distinct groups** with **separate permissions and dashboards**. Access is enforced through:

1. **Decorator-based role checks** before each view executes
2. **Role-specific authentication** with different credential types
3. **Resource ownership verification** to prevent unauthorized access
4. **URL isolation** per role with separate apps and namespaces

The system is effective for simple three-role scenarios but would benefit from Django's `django-guardian` package for more complex permission requirements.
