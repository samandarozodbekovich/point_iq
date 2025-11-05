from django.db import models

from apps.citizens.population.models import Population
from apps.shared.models import BaseTimeModel, BaseNameModel


class Religion(BaseNameModel,BaseTimeModel):

    def __str__(self):
        return self.name_uz


class ReligionCount(BaseTimeModel):
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    religion = models.ForeignKey(Religion, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.count} people at ({self.religion.name_uz})"



