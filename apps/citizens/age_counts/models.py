from django.db import models
from django.core.validators import MinValueValidator

from apps.areas.places.models import Place
from apps.citizens.age_groups.models import AgeGroup
from apps.shared.models import BaseTimeModel


class PopulationStatistic(BaseTimeModel):

    apartment = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="population_statistics"
    )
    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.CASCADE,
        related_name="population_statistics"
    )
    population_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "Population Statistic"
        verbose_name_plural = "Population Statistics"


    def __str__(self):
        return f"{self.apartment.name_uz} | {self.age_group.name_uz}: {self.population_count}"