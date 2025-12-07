from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.areas.districts.models import District
from apps.dictionary.crimes.crime_types.models import CrimeTypes
from apps.shared.models import BaseTimeModel


class CrimeStatistics(BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.SET_NULL , null=True, blank=True)
    crime = models.ForeignKey(CrimeTypes, on_delete=models.SET_NULL , null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)

