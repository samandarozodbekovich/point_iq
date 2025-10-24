from django.db import models

from apps.areas.cities.models import City
from apps.shared.models import BaseNameModel, BaseTimeModel


class District(BaseNameModel, BaseTimeModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name_uz} ({self.city.name_uz})"