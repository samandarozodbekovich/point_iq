from django.db import models

from apps.areas.districts.models import District
from apps.dictionary.devices.device_data.models import DeviceData


class FootfallEvent(models.Model):
    device = models.ForeignKey(DeviceData, on_delete=models.CASCADE, related_name='footfall_events')
    location = models.ForeignKey(District, on_delete=models.CASCADE, related_name='footfall_events')
    timestamp = models.DateTimeField()
    dwell_time_minutes = models.IntegerField(default=0)