from django.db import models

from apps.citizens.population.models import Population
from apps.shared.models import BaseTimeModel


class AgeGroup(BaseTimeModel):
    age_group = models.CharField(max_length=15,null=True,blank=True, unique=True)

    class Meta:
        verbose_name = "Age Group"
        verbose_name_plural = "Age Groups"
        ordering = ["id"]

    def __str__(self):
        return self.age_group


class AgeGroupPopulation(BaseTimeModel):
    population = models.ForeignKey(Population,on_delete=models.CASCADE)
    age_group = models.ForeignKey(AgeGroup,on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    class Meta:
        verbose_name = "Age Group Population"
        verbose_name_plural = "Age Group Populations"

    def __str__(self):
        return f"{self.population__district__name_uz} - {self.age_group}"

