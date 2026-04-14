from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='organizer_dashboard'),
    path('create/', views.create_event, name='create_event'),
    path('edit/<int:pk>/', views.edit_event, name='edit_event'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('checkin/<int:reg_pk>/', views.checkin_student, name='checkin_student'),
    path('announce/', views.send_announcement, name='send_announcement'),
    path('certificate/<int:reg_pk>/', views.issue_certificate, name='issue_certificate'),
    path('analytics/', views.analytics, name='organizer_analytics'),
]
