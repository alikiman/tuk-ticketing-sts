# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return account_views.home(request)


urlpatterns = [
    
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('tickets/', include('tickets.urls')),
    
    # ✅ Notifications namespace securely integrated
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)