from django.db import models

from apps.government_bodies.models.government_body import GovernmentBody
from apps.shared.models import BaseTimeModel, BaseNameModel


class GovernmentWorker(BaseNameModel,BaseTimeModel):
    government = models.ForeignKey(GovernmentBody, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=50)
    phone_number = models.TextField(max_length=20)
    work_day = models.CharField(max_length=50)
    work_time = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name_uz} works at {self.government.address}"