# notifications/context_processors.py
from .models import Notification

def unread_notifications_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(user=request.user, is_read=False).count()
        }
    return {'unread_notifications_count': 0}

from .models import Notification

def notification_context(request):
    """
    Makes the unread notification count globally available to all templates.
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
        
    return {
        'unread_notifications_count': count
    }