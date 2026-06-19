from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from django.db.models import Count, Q

from tickets.models import Ticket
from .forms import RegisterForm, StaffCreationForm

User = get_user_model()


def home(request):
    return render(request, "home.html")


# =====================================================
# 🔐 HELPERS (CLEAN ACCESS CONTROL)
# =====================================================

def is_admin(user):
    return user.is_superuser

def is_staff(user):
    return getattr(user, "role", None) == "staff"

def is_student(user):
    return getattr(user, "role", None) == "student"

def deny_redirect(user):
    return redirect("accounts:dashboard_redirect")


# =====================================================
# LOGIN & LOGOUT
# =====================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard_redirect")

    # Clear old messages
    storage = get_messages(request)
    for _ in storage:
        pass

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session.save()  # Ensure session stability
            return redirect("accounts:dashboard_redirect")
        
        messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect("accounts:login")


# =====================================================
# REGISTER (STUDENTS ONLY)
# =====================================================

def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard_redirect")

    form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "student"
            user.is_staff = False
            user.save()
            messages.success(request, "Account created successfully.")
            return redirect("accounts:login")

    return render(request, "registration/register.html", {"form": form})


# =====================================================
# ROLE REDIRECT (CENTRAL ROUTER)
# =====================================================

@login_required
def role_redirect(request):
    user = request.user
    if is_admin(user):
        return redirect("accounts:admin_dashboard")
    if is_staff(user):
        return redirect("accounts:staff_dashboard")
    return redirect("accounts:student_dashboard")


# =====================================================
# ADMIN DASHBOARDS & MANAGEMENT
# =====================================================

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return deny_redirect(request.user)

    all_tickets = Ticket.objects.all().order_by('-created_at')

    return render(request, "dashboard/admin.html", {
        "tickets": all_tickets,
        "total_users": User.objects.count(),
        "ticket_stats": Ticket.objects.aggregate(
            total=Count('id'),
            open=Count('id', filter=Q(status='open')),
            resolved=Count('id', filter=Q(status='resolved'))
        )
    })


@login_required
def admin_users(request):
    if not is_admin(request.user):
        return deny_redirect(request.user)

    return render(request, "dashboard/admin_users.html", {
        "users": User.objects.all().order_by("-date_joined")
    })


@login_required
def admin_tickets(request):
    if not is_admin(request.user):
        return deny_redirect(request.user)

    return render(request, "dashboard/admin_tickets.html", {
        "tickets": Ticket.objects.all().order_by("-created_at")
    })


@login_required
def create_staff(request):
    if not is_admin(request.user):
        return deny_redirect(request.user)

    form = StaffCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Staff created successfully.")
        return redirect("accounts:admin_dashboard")

    return render(request, "registration/create_staff.html", {"form": form})


@login_required
def assign_ticket(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Only admins can assign tickets.")
        return redirect("accounts:dashboard_redirect")

    ticket = get_object_or_404(Ticket, pk=pk)
    staff_users = User.objects.filter(role="staff")

    if request.method == "POST":
        staff_id = request.POST.get("staff_id")
        staff = get_object_or_404(User, pk=staff_id, role="staff")

        ticket.assigned_to = staff
        ticket.status = "assigned"
        ticket.save()

        messages.success(request, "Ticket assigned successfully.")
        return redirect("accounts:admin_tickets")

    return render(request, "dashboard/assign_ticket.html", {
        "ticket": ticket,
        "staff_users": staff_users
    })


@login_required
def archive_ticket(request, ticket_id):
    if request.method == "POST":
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.delete()
    return redirect('accounts:admin_dashboard')


# =====================================================
# STAFF DASHBOARD & ACTIONS
# =====================================================

@login_required
def staff_dashboard(request):
    if not is_staff(request.user):
        return deny_redirect(request.user)

    # Grabs tickets assigned to this staff user OR completely unassigned tickets
    tickets = Ticket.objects.filter(
        Q(assigned_to=request.user) | Q(assigned_to__isnull=True)
    ).order_by('-created_at')

    # Normalize 'open' statuses to 'assigned' temporarily for template-side JS tab filters
    for ticket in tickets:
        if ticket.status == 'open':
            ticket.status = 'assigned'

    return render(request, "dashboard/staff.html", {
        "assigned_tickets": tickets
    })


@login_required
def staff_update_status(request, pk):
    if not is_staff(request.user):
        return deny_redirect(request.user)

    ticket = get_object_or_404(Ticket, pk=pk)

    # Implicitly claim ticket if it was totally unassigned
    if ticket.assigned_to is None:
        ticket.assigned_to = request.user
    elif ticket.assigned_to != request.user:
        messages.error(request, "You are not authorized to update this ticket.")
        return redirect("accounts:staff_dashboard")

    if request.method == "POST":
        new_status = request.POST.get("status")
        allowed_statuses = ["assigned", "in_progress", "resolved", "closed"]

        if new_status in allowed_statuses:
            ticket.status = new_status
            ticket.save()
            messages.success(request, f"Ticket status changed to {new_status.replace('_', ' ').title()}.")
        else:
            messages.error(request, "Invalid status string submitted.")

    return redirect("accounts:staff_dashboard")


# =====================================================
# STUDENT DASHBOARD & PROFILE
# =====================================================

@login_required
def student_dashboard(request):
    if not is_student(request.user):
        return deny_redirect(request.user)

    return render(request, "dashboard/student.html", {
        "tickets": Ticket.objects.filter(student=request.user)
    })


@login_required
def profile(request):
    user = request.user
    
    if request.method == "POST":
        if "profile_pic" in request.FILES:
            user.profile_pic = request.FILES["profile_pic"]
            user.save()
            return redirect("accounts:profile") 
            
    return render(request, "registration/profiles.html", {
        "user": user
    })