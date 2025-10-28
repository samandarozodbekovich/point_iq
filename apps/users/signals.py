from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.users.models.user import User, NEW
from apps.users.tasks import send_registration_email

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created or instance.auth_status == NEW:
        code = instance.create_verify_code()
        transaction.on_commit(lambda: send_registration_email.delay(instance.email, code))



