from django.db import models

from apps.citizens.population.models import Population
from apps.shared.models import BaseTimeModel, BaseNameModel


class RelationshipStatus(BaseTimeModel, BaseNameModel):

    def __str__(self):
        return self.name_uz


class RelationshipStatusPopulation(BaseTimeModel):
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    relationship_status = models.ForeignKey(RelationshipStatus, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.population} - {self.relationship_status}"

