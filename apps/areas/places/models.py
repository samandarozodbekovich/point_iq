from django.db import models

from apps.areas.streets.models import Street
from apps.shared.models import BaseNameModel, BaseTimeModel

class Place(BaseNameModel, BaseTimeModel):
    street = models.ForeignKey(Street, on_delete=models.CASCADE, related_name="apartments")
    house_number = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['street', 'house_number']

    def __str__(self):
        return f"{self.name_uz or self.house_number} ({self.street.name_uz})"

    @property
    def full_address(self):
        return f"{self.street.name_uz}, {self.street.area.name_uz}, {self.street.area.district.name_uz}, {self.street.area.city.name_uz}"
