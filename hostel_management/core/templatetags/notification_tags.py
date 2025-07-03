from django import template
from core.models import Notification

register = template.Library()

@register.simple_tag
def get_unread_notifications_count(user):
    """Return the count of unread notifications for a user."""
    return Notification.objects.filter(recipients=user).exclude(read_by=user).count()