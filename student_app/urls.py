from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('discover/', views.discover_events, name='discover_events'),
    path('register/<int:pk>/', views.register_event, name='register_event'),
    path('ticket/<int:pk>/', views.my_ticket, name='my_ticket'),
    path('my-events/', views.my_events, name='my_events'),
    path('certificates/', views.certificates, name='student_certificates'),
    path('cancel/<int:pk>/', views.cancel_registration, name='cancel_registration'),
    path('feedback/<int:event_pk>/', views.submit_feedback, name='submit_feedback'),
]
