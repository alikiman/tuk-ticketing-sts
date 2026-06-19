from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),

    path('create/', views.ticket_create, name='ticket_create'),

    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),

    path('<int:pk>/status/', views.update_ticket_status, name='update_ticket_status'),

    path('assign/<int:pk>/', views.assign_ticket, name='assign_ticket'),
]