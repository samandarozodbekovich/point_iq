from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.areas.districts.models import District
from apps.dictionary.crimes.crime_types.models import CrimeTypes
from apps.shared.models import BaseTimeModel


class CrimeStatistics(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    crime = models.ForeignKey(CrimeTypes, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)

