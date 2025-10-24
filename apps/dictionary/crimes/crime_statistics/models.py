from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from apps.areas.areas.models import Area
from apps.dictionary.crimes.crime_types.models import CrimeTypes
from apps.shared.models import BaseTimeModel


class CrimeStatistics(BaseTimeModel):
    crime = models.ForeignKey(CrimeTypes, on_delete=models.CASCADE)
    area = models.ForeignKey(Area,on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)

