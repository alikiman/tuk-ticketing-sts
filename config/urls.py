# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    # Automatically routes visitors landing on http://127.0.0.1:8000/ to the login screen
    return redirect('accounts:login')


urlpatterns = [
    # Changed from account_views.home to local home function for the clean login redirect
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('tickets/', include('tickets.urls')),
    
    # ✅ Notifications namespace securely integrated
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)