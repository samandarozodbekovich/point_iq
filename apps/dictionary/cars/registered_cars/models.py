from django.db import models

from apps.areas.districts.models import District
from apps.dictionary.cars.car_type.models import CarType
from apps.shared.models import BaseTimeModel


class RegisteredCar(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL , null=True, blank=True)
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)
    registered_count = models.IntegerField()
    source = models.CharField(max_length=100)