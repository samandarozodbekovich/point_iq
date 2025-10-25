from django.db import models
from apps.areas.places.models import Place
from apps.shared.models import BaseTimeModel


class Citizen(BaseTimeModel):
    apartment = models.ForeignKey(Place, on_delete=models.CASCADE)
    count_male = models.IntegerField(default=0)
    count_female = models.IntegerField(default=0)
    average_income = models.DecimalField(max_digits=10, decimal_places=2)
    unemployment_rate = models.DecimalField(max_digits=4, decimal_places=2)
    population_density = models.IntegerField()


