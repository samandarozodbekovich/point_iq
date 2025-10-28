from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.areas.cities.models import City
from apps.areas.districts.models import District
from apps.shared.models import BaseNameModel, BaseTimeModel

class Area(BaseNameModel, BaseTimeModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    wealthy_area_rating = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])


    def __str__(self):
        return f"{self.name_uz} ({self.district.name_uz})"

    class Meta:
        unique_together = ('name_uz', 'district')
        ordering = ['name_uz']


