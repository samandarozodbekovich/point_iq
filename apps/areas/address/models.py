from django.db import models

from apps.shared.models import BaseNameModel, BaseTimeModel
from apps.areas.districts.models import District

class Address(BaseNameModel, BaseTimeModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='address')


    def __str__(self):
        return f"{self.name_uz} ({self.district.name_uz})"

