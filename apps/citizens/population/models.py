from django.db import models
from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel


class Population(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    count_male = models.FloatField(default=0)
    count_female = models.FloatField(default=0)
    average_income = models.FloatField(default=0)
    unemployment_rate = models.FloatField(default=0)
    population_density = models.FloatField(default=0)
    birth_rate = models.FloatField(default=0)
    death_rate = models.FloatField(default=0)
    immigration_count = models.IntegerField(default=0)
    emission_count = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.population_density} in {self.district.name_uz}"

