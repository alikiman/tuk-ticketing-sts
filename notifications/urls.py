from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path('', views.notification_list, name='notifications'),
    path('read/<int:pk>/', views.mark_as_read, name='notification-read'),
    path('read-all/', views.mark_all_as_read, name='notification-read-all'),
    path('api/unread-count/', views.unread_notification_count_api, name='unread_count_api'),
]