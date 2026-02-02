from django.db import models

from apps.citizens.population.models import Population
from apps.shared.models import BaseTimeModel, BaseNameModel


class RelationshipStatus(BaseTimeModel, BaseNameModel):

    def __str__(self):
        return self.name_uz


class RelationshipStatusPopulation(BaseTimeModel):
    population = models.ForeignKey(Population, on_delete=models.SET_NULL , null=True, blank=True)
    relationship_status = models.ForeignKey(RelationshipStatus, on_delete=models.SET_NULL , null=True, blank=True)
    count = models.IntegerField(default=0)


