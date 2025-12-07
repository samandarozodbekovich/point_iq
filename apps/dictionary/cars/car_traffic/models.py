from django.db import models

from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel


class CarTraffic(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    date_recorded = models.DateField()
    average_daily_cars = models.IntegerField()
    peak_hour = models.CharField(max_length=20)
    congestion_level = models.CharField(max_length=20)
    source = models.CharField(max_length=100)