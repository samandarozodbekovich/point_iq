from django.db import models
from django.contrib.gis.db import models as geo_models

from apps.shared.models import BaseTimeModel


class PointOfInterestModel(BaseTimeModel):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    location = geo_models.PointField(srid=4326)
    influence_radius = models.FloatField(help_text="Radius of influence(metr)")
    attraction_factor = models.FloatField(default=0.1)

    external_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return self.name