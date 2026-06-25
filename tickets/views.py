from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Ticket, TicketResponse
from .forms import TicketForm, TicketResponseForm

# Import the Notification model from your notifications application
from notifications.models import Notification

User = get_user_model()


# =====================================
# TICKET LIST
# =====================================
@login_required
def ticket_list(request):
    user = request.user
    status_filter = request.GET.get("status")

    if user.role == "student":
        tickets = Ticket.objects.filter(student=user)
    elif user.role == "staff":
        tickets = Ticket.objects.filter(assigned_to=user)
    elif user.role == "admin":
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.none()

    # FILTER SUPPORT
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    return render(request, "tickets/ticket_list.html", {
        "tickets": tickets
    })


# =====================================
# CREATE TICKET
# =====================================
@login_required
def ticket_create(request):
    if request.user.role != "student":
        messages.error(request, "Only students can create tickets.")
        return redirect("tickets:ticket_list")

    form = TicketForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.student = request.user
        ticket.status = "assigned"
        ticket.save()

        # AUTO ASSIGN
        ticket.route_to_staff()

        # EMAIL NOTIFICATION TO STUDENT
        if request.user.email:
            send_mail(
                subject="Ticket Submitted Successfully",
                message=(
                    f"Hello {request.user.username},\n\n"
                    f"Your ticket '{ticket.title}' has been received successfully.\n\n"
                    f"Tracking ID: #{ticket.pk}\n"
                    f"Category: {ticket.category}\n"
                    f"Status: {ticket.status.replace('_', ' ').title()}\n\n"
                    f"We will notify you once there is an update.\n\n"
                    f"Thank you for using the TUK Ticketing System."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

        # IN-APP NOTIFICATION FOR STUDENT
        Notification.objects.create(
            user=request.user,
            message=f"Ticket '{ticket.title}' successfully submitted. Tracking ID: #{ticket.pk}."
        )

        # IN-APP NOTIFICATION FOR STAFF
        if ticket.assigned_to:
            Notification.objects.create(
                user=ticket.assigned_to,
                message=f"New ticket #{ticket.pk} ('{ticket.title}') has been assigned to you."
            )

        messages.success(request, "Ticket created successfully.")
        return redirect("tickets:ticket_list")

    return render(request, "tickets/create_ticket.html", {"form": form})


# =====================================
# TICKET DETAIL (WITH IN-APP MESSAGING HOOKS)
# =====================================
@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Security Check: Ensure only the ticket owner or staff can view/reply
    if not (request.user.is_superuser or request.user.role == 'staff' or ticket.student == request.user):
        return redirect('tickets:ticket_list')

    if request.method == 'POST':
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response_obj = form.save(commit=False)
            response_obj.ticket = ticket
            response_obj.responder = request.user  
            response_obj.save()
            
            # Reset status back to "open" or "in_progress" if student replies to a resolved ticket
            if request.user == ticket.student and ticket.status == 'resolved':
                ticket.status = 'open'
                ticket.save()

            # ✅ UPDATED: Messaging notifications logic
            if request.user.role == "staff" or request.user.is_superuser:
                # Notify student when a staff member sends a message in-app
                Notification.objects.create(
                    user=ticket.student,
                    message=f"Staff member {request.user.username} sent you a message regarding Ticket #{ticket.pk}."
                )
            elif request.user == ticket.student and ticket.assigned_to:
                # Notify staff when the student replies back
                Notification.objects.create(
                    user=ticket.assigned_to,
                    message=f"Student {request.user.username} submitted a new reply to Ticket #{ticket.pk}."
                )
                
            return redirect('tickets:ticket_detail', pk=ticket.pk)
    else:
        form = TicketResponseForm()

    responses = ticket.responses.all().order_by('created_at')

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'form': form
    })


# =====================================
# UPDATE TICKET STATUS
# =====================================
@login_required
def update_ticket_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user

    if user.role != "staff":
        messages.error(request, "Not allowed.")
        return redirect("tickets:ticket_list")

    if ticket.assigned_to != user:
        messages.error(request, "This ticket is not assigned to you.")
        return redirect("tickets:ticket_list")

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in ["in_progress", "resolved", "closed"]:
            ticket.status = new_status
            ticket.save()

            # Notify the student their ticket state changed
            Notification.objects.create(
                user=ticket.student,
                message=f"Your ticket #{ticket.pk} status has been updated to '{new_status.replace('_', ' ').title()}'."
            )

            messages.success(request, "Status updated successfully.")
        else:
            messages.error(request, "Invalid status.")

    return redirect("tickets:ticket_detail", pk=ticket.pk)


# =====================================
# ASSIGN TICKET
# =====================================
@login_required
def assign_ticket(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Only admins can assign tickets.")
        return redirect("tickets:ticket_list")

    ticket = get_object_or_404(Ticket, pk=pk)
    staff_id = request.POST.get("staff_id")

    if staff_id:
        staff = get_object_or_404(User, pk=staff_id, role="staff")
    else:
        staff = User.objects.filter(role="staff").first()

    if not staff:
        messages.error(request, "No staff available.")
        return redirect("tickets:ticket_list")

    ticket.assigned_to = staff
    ticket.status = "assigned"
    ticket.save()

    # Notify both the staff member and the student
    Notification.objects.create(
        user=staff,
        message=f"Ticket #{ticket.pk} ('{ticket.title}') has been assigned to you."
    )
    Notification.objects.create(
        user=ticket.student,
        message=f"Your ticket #{ticket.pk} has been assigned to staff member: {staff.username}."
    )

    messages.success(request, f"Assigned to {staff.username}")
    return redirect("tickets:ticket_detail", pk=pk)