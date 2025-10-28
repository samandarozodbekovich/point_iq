from django.db import models
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User


class UserConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verify_codes')
    code = models.CharField(max_length=4)
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expiration_time = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expiration_time

    def __str__(self):
        return f"{self.user.email} - {self.code}"
