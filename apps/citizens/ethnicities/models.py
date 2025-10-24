from django.db import models

from apps.areas.places.models import Place
from apps.shared.models import BaseNameModel, BaseTimeModel


class Ethnicity(BaseNameModel, BaseTimeModel):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_uz
