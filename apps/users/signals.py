from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.users.models import User
from apps.users.tasks import send_registration_email

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        code = instance.create_verify_code()
        send_registration_email.delay(instance.email, code)
