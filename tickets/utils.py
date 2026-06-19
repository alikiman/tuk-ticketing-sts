from django.db.models import Count
from .models import Ticket


def get_category_stats(user=None):
    """
    Returns ticket counts per category.
    If user is provided, filters based on role.
    """

    tickets = Ticket.objects.all()

    # Filter by role if user is provided
    if user:

        if user.role == "student":
            tickets = tickets.filter(student=user)

        elif user.role == "staff":
            tickets = tickets.filter(assigned_to=user)

        # admin sees everything (no filter)

    stats = (
        tickets.values('category')
        .annotate(total=Count('id'))
        .order_by()
    )

    return {
        item['category']: item['total']
        for item in stats
    }

def status_color(status):
    colors = {
        "open": "gray",
        "assigned": "blue",
        "in_progress": "orange",
        "resolved": "green",
        "closed": "black",
    }
    return colors.get(status, "gray")