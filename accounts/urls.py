from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import (
    register,
    role_redirect,
    login_view,
    admin_dashboard,
    staff_dashboard,
    student_dashboard,
    admin_users,
    admin_tickets,
    create_staff,
    assign_ticket,
    custom_logout,
    profile,
)

app_name = "accounts"

urlpatterns = [
    # AUTH
    path("logout/", custom_logout, name="logout"),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),

    # ROOT
    path("", role_redirect, name="home"),
    path("redirect/", role_redirect, name="dashboard_redirect"),

    # DASHBOARDS
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("staff-dashboard/", staff_dashboard, name="staff_dashboard"),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("profile/", profile, name="profile"),
    # ADMIN FEATURES
    path("admin-users/", admin_users, name="admin_users"),
    path("admin-tickets/", admin_tickets, name="admin_tickets"),
    path("create-staff/", create_staff, name="create_staff"),
    path("assign-ticket/<int:pk>/", assign_ticket, name="assign_ticket"),
    path('archive-ticket/<int:ticket_id>/', views.archive_ticket, name='archive_ticket')
]