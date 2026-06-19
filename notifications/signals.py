# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from tickets.models import Ticket
from .models import Notification

@receiver(post_save, sender=Ticket)
def ticket_notification_handler(sender, instance, created, **kwargs):
    """
    Automatically generates real-time notifications when a ticket is assigned or updated.
    """
    if created:
        # If a student created a ticket, notify admins (or handle student initial receipt)
        # Assuming you want to notify the student that their ticket was received:
        if instance.student:
            Notification.objects.create(
                user=instance.student,
                message=f"Your ticket #{instance.id} ('{instance.title}') has been successfully created."
            )
    else:
        # Check if the ticket status changed or a staff member was assigned
        # 1. Notify the staff member they've been assigned a ticket
        if instance.assigned_to and instance.status == "assigned":
            # Avoid duplicating identical unread notifications if saved multiple times
            Notification.objects.get_or_create(
                user=instance.assigned_to,
                message=f"You have been assigned Ticket #{instance.id}: '{instance.title}'.",
                is_read=False
            )
            
        # 2. Notify the student about updates (In Progress, Resolved, Closed)
        if instance.student and instance.status in ["in_progress", "resolved", "closed"]:
            readable_status = instance.status.replace('_', ' ').title()
            Notification.objects.create(
                user=instance.student,
                message=f"The status of your ticket #{instance.id} has been updated to: {readable_status}."
            )