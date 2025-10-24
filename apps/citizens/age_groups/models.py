from django.db import models

from apps.areas.places.models import Place
from apps.shared.models import BaseNameModel, BaseTimeModel


class AgeGroup(BaseNameModel, BaseTimeModel):

    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Age Group"
        verbose_name_plural = "Age Groups"
        ordering = ["id"]

    def __str__(self):
        return self.name_uz


