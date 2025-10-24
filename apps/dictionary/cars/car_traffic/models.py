from django.db import models

from apps.areas.areas.models import Area
from apps.areas.streets.models import Street
from apps.shared.models import BaseTimeModel


class CarTraffic(BaseTimeModel):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='car_traffic')
    street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, blank=True)
    date_recorded = models.DateField()
    average_daily_cars = models.IntegerField()
    peak_hour = models.CharField(max_length=20)
    congestion_level = models.CharField(max_length=20)
    source = models.CharField(max_length=100)