from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('organizer/', include('organizer_app.urls')),
    path('student/', include('student_app.urls')),
    path('admin-panel/', include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
