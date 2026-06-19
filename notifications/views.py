from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

# =========================
# LIST & MARK ALL AS READ (COMBINED HTTP & AJAX)
# =========================
@login_required
def notification_list(request):
    # If the frontend script sends a background POST request to this view,
    # mark all unread notifications as read immediately.
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})

    # Regular GET request displays the notifications page layout
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request,
        "notifications/list.html", # Verify this filename matches your path (e.g., notification.html)
        {"notifications": notifications}
    )

# =========================
# MARK AS READ (INDIVIDUAL)
# =========================
@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect("notifications:notifications")

# =========================
# MARK ALL AS READ (FALLBACK REDIRECT ROUTE)
# =========================
@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:notifications")

# =========================
# LIVE BADGE API ENDPOINT
# =========================
@login_required
def unread_notification_count_api(request):
    """
    Returns the real-time unread notifications count for the currently logged-in user.
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})