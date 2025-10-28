from django.db import models

from apps.citizens.population.models import Population
from apps.citizens.religions.models import Religion
from apps.shared.models import BaseNameModel, BaseTimeModel


class ReligionCount(BaseTimeModel):
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    religion = models.ForeignKey(Religion, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.religion.name_uz} {self.count} people"
