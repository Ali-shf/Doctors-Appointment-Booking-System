from django import template
from reservation.models import Visit

register = template.Library()

@register.filter
def has_visited(user, doctor):
    """
    Return True if the user has visited the doctor at least once.
    user: User instance (authenticated)
    doctor: Doctor instance
    """
    if not user.is_authenticated:
        return False
    return Visit.objects.filter(patient=user, doctor=doctor).exists()
