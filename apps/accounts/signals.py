from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EmployeeProfile, User


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    """Todo usuario nuevo recibe automáticamente su perfil de empleado."""
    if created:
        EmployeeProfile.objects.get_or_create(user=instance)
