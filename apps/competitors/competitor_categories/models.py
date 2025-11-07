from django.db import models

from apps.shared.models import BaseNameModel, BaseTimeModel


class CompetitorCategory(BaseNameModel, BaseTimeModel):
    external_id = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.name_uz

