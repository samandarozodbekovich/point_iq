from django.db import models

from apps.shared.models import BaseNameModel, BaseTimeModel


# Create your models here.

class GovernmentBody(BaseNameModel, BaseTimeModel):
    description = models.TextField()
    address = models.CharField(max_length=50)
    schedule = models.CharField(max_length=50)
    phone_number = models.TextField(max_length=20)
    email = models.EmailField(max_length=50, null=True, blank=True)
    director = models.CharField(max_length=50)
    longitude = models.FloatField(max_length=50, null=True, blank=True)
    latitude = models.FloatField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name_uz} is located at {self.address}"



