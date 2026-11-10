from django.contrib.gis.db import models as geo_models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from apps.shared.models import BaseTimeModel

class TrafficNodeModel(BaseTimeModel):
    NODE_TYPES = (
    ('transit', 'Transit (Metro station)'),
    ('target', 'Target (Bozor, Mall)'),
    ('local', 'Lokal (Turar joy)')
    )
    name = models.CharField(max_length=255)
    location = geo_models.PointField(srid=4326)
    node_type = models.CharField(max_length=20, choices=NODE_TYPES)
    base_weight = models.IntegerField(validators=([MinValueValidator(1),MaxValueValidator(10)]), default=1)

    # guess daily flow
    manual_flow_estimate = models.IntegerField(null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.name} {self.node_type}"