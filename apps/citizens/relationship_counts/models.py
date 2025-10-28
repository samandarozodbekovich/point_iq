from django.db import models

from apps.citizens.population.models import Population
from apps.citizens.relationship_status.models import RelationshipStatus
from apps.shared.models import BaseTimeModel


class RelationshipCount(BaseTimeModel):
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    relationship_status = models.ForeignKey(RelationshipStatus, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.count} at {self.relationship_status.name_uz}"

