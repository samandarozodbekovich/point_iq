from django.db import models

from apps.citizens.ethnicities.models import Ethnicity
from apps.shared.models import BaseTimeModel


class EthnicityCount(BaseTimeModel):
    ethnicity = models.ForeignKey(Ethnicity, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)