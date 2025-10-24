from django.db import models

from apps.citizens.relationship_status.models import RelationshipStatus
from apps.shared.models import BaseTimeModel


class RelationshipCount(BaseTimeModel):
    category = models.ForeignKey(RelationshipStatus, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.count} at {self.category.name_uz}"

