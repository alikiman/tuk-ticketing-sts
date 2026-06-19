from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Ticket(models.Model):

    CATEGORY_CHOICES = (
        ('academic', 'Academic'),
        ('clearance', 'Clearance'),
        ('fees', 'Fees'),
        ('results', 'Results'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # UPDATED: Changed default from 'open' to 'assigned' to sync seamlessly with staff views
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='assigned'
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def assign_to(self, staff_user):
        self.assigned_to = staff_user
        self.status = "assigned"
        self.save()

    def mark_in_progress(self):
        self.status = "in_progress"
        self.save()

    def mark_resolved(self):
        self.status = "resolved"
        self.save()

    def mark_closed(self):
        self.status = "closed"
        self.save()

    def route_to_staff(self):
        staff = User.objects.filter(role="staff").first()

        if staff:
            self.assigned_to = staff
            self.status = "assigned"
            self.save()

    def __str__(self):
        return self.title


class TicketResponse(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Response for {self.ticket.title}"