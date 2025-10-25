from django.db import models

from apps.areas.areas.models import Area
from apps.shared.models import BaseNameModel, BaseTimeModel

class Street(BaseNameModel, BaseTimeModel):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='streets')


    def __str__(self):
        return f"{self.name_uz} ({self.area.name_uz})"

