from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('pending/', views.pending_events, name='admin_pending'),
    path('events/', views.all_events, name='admin_all_events'),
    path('events/<int:pk>/review/', views.review_event, name='review_event'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:pk>/toggle/', views.toggle_user, name='toggle_user'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),
    path('cert/<int:reg_pk>/issue/', views.issue_cert_admin, name='issue_cert_admin'),
]
