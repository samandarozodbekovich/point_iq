from django.db import models

from apps.areas.address.models import Address
from apps.shared.models import BaseTimeModel


class DeviceData(BaseTimeModel):
    home_location = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='devices')