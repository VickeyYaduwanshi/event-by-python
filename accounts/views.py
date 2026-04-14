from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
import hashlib

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    role = request.GET.get('role', 'student')
    
    if request.method == 'POST':
        role_post = request.POST.get('role', 'student')
        password = request.POST.get('password')
        
        # Admin login - hardcoded
        if role_post == 'admin':
            username_input = request.POST.get('username', '').strip()
            # Accept both "219" and "user-219"
            if not username_input.startswith('user-'):
                username_input = f'user-{username_input}'
            
            if username_input == 'user-219' and password == '8120':
                # Get or create admin user
                admin_user, created = User.objects.get_or_create(
                    username='admin_user',
                    defaults={'email': 'admin@collegeevents.com', 'is_staff': True, 'is_superuser': True}
                )
                if created:
                    admin_user.set_password('8120')
                    admin_user.save()
                    UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
                
                login(request, admin_user)
                return redirect('/admin-panel/dashboard/')
            else:
                messages.error(request, 'Invalid admin credentials.')
        
        # Student login - enrollment number + password
        elif role_post == 'student':
            enrollment = request.POST.get('username')
            try:
                profile = UserProfile.objects.get(enrollment_number=enrollment, role='student')
                user = profile.user
                if user.check_password(password):
                    login(request, user)
                    return redirect_by_role(user)
                else:
                    messages.error(request, 'Invalid enrollment number or password.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Invalid enrollment number or password.')
        
        # Organizer login - Gmail + password
        elif role_post == 'organizer':
            email = request.POST.get('username')
            try:
                user = User.objects.get(email=email)
                profile = user.profile
                if profile.role == 'organizer' and user.check_password(password):
                    login(request, user)
                    return redirect_by_role(user)
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html', {'role': role})

def redirect_by_role(user):
    try:
        profile = user.profile
        if profile.role == 'admin' or user.is_superuser:
            return redirect('/admin-panel/dashboard/')
        elif profile.role == 'organizer':
            return redirect('/organizer/dashboard/')
        else:
            return redirect('/student/dashboard/')
    except UserProfile.DoesNotExist:
        if user.is_superuser:
            return redirect('/admin-panel/dashboard/')
        return redirect('/')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('/')

def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'student')
        email = request.POST.get('email')
        name = request.POST.get('name', '')
        department = request.POST.get('department', '')
        branch = request.POST.get('branch', '')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'role': role})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html', {'role': role})
        
        if role == 'student':
            enrollment = request.POST.get('enrollment_number')
            if UserProfile.objects.filter(enrollment_number=enrollment).exists():
                messages.error(request, 'Enrollment number already registered.')
                return render(request, 'accounts/register.html', {'role': role})
            
            # Create user with email as username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            UserProfile.objects.create(
                user=user,
                role='student',
                enrollment_number=enrollment,
                department=department,
                branch=branch
            )
        
        elif role == 'organizer':
            # Create user with email as username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            UserProfile.objects.create(
                user=user,
                role='organizer',
                department=department,
                branch=branch
            )
        
        messages.success(request, 'Account created! Please login.')
        return redirect(f'/accounts/login/?role={role}')
    
    role = request.GET.get('role', 'student')
    return render(request, 'accounts/register.html', {'role': role})
