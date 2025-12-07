from django.db import models

from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel


class DeviceData(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    home_location = models.CharField(max_length=100, null=True, blank=True)