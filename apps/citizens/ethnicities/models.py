from django.db import models

from apps.citizens.population.models import Population
from apps.shared.models import BaseNameModel, BaseTimeModel


class Ethnicity(BaseNameModel, BaseTimeModel):


    def __str__(self):
        return self.name_uz


class EthnicityPopulation(BaseTimeModel):
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    ethnicity = models.ForeignKey(Ethnicity, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.population