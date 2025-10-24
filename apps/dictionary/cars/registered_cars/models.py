from django.db import models

from apps.areas.streets.models import Street
from apps.dictionary.cars.car_type.models import CarType
from apps.shared.models import BaseTimeModel


class RegisteredCar(BaseTimeModel):
    street = models.ForeignKey(Street, on_delete=models.CASCADE)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)
    registered_count = models.IntegerField()
    source = models.CharField(max_length=100)