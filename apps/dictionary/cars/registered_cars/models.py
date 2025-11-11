from django.db import models

from apps.areas.address.models import Address
from apps.dictionary.cars.car_type.models import CarType
from apps.shared.models import BaseTimeModel


class RegisteredCar(BaseTimeModel):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)
    registered_count = models.IntegerField()
    source = models.CharField(max_length=100)