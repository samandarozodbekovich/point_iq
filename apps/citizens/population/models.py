from django.db import models
from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel


class Population(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    count_male = models.IntegerField(default=0)
    count_female = models.IntegerField(default=0)
    average_income = models.DecimalField(max_digits=10, decimal_places=2)
    unemployment_rate = models.DecimalField(max_digits=4, decimal_places=2)
    population_density = models.IntegerField()
    birth_rate = models.IntegerField()
    death_rate = models.IntegerField()
    immigration_count = models.IntegerField()
    emission_count = models.IntegerField()


    def __str__(self):
        return f"{self.population_density} in {self.district.name_uz}"

