from django.db import models

from apps.areas.address.models import Address
from apps.shared.models import BaseTimeModel


class CarTraffic(BaseTimeModel):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    date_recorded = models.DateField()
    average_daily_cars = models.IntegerField()
    peak_hour = models.CharField(max_length=20)
    congestion_level = models.CharField(max_length=20)
    source = models.CharField(max_length=100)