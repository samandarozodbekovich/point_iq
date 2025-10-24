from django.db import models

from apps.areas.areas.models import Area
from apps.shared.models import BaseTimeModel


class DeviceData(BaseTimeModel):
    device_uid = models.CharField(max_length=255, unique=True)
    home_location = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, related_name='devices')