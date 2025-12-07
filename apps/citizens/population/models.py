from django.db import models
from apps.areas.districts.models import District
from apps.shared.models import BaseTimeModel


class Population(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    count_male = models.FloatField()
    count_female = models.FloatField()
    average_income = models.FloatField()
    unemployment_rate = models.FloatField()
    population_density = models.FloatField()
    birth_rate = models.FloatField()
    death_rate = models.FloatField()
    immigration_count = models.IntegerField()
    emission_count = models.IntegerField()


    def __str__(self):
        return f"population density: {self.population_density} in {self.district.name_uz}"

