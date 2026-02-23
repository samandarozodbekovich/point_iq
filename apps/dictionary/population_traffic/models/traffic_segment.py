from django.db import models
from django.contrib.gis.db import models as geo_models

from apps.shared.models import BaseTimeModel


class TrafficSegmentModel(BaseTimeModel):
    line = geo_models.LineStringField(srid=4326)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    intensity_level = models.CharField(max_length=50)
    zone_color = models.CharField(max_length=50, default="green")
    rank_percentile = models.FloatField(null=True, blank=True)

    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return self.street_name