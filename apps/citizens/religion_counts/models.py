from django.db import models

from apps.citizens.religions.models import Religion
from apps.shared.models import BaseNameModel, BaseTimeModel


class ReligionCount(BaseNameModel, BaseTimeModel):
    religion = models.ForeignKey(Religion, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.religion.name_uz} {self.count} people"
