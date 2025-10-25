from django.db import models

from apps.citizens.ethnicities.models import Ethnicity
from apps.citizens.population.models import Citizen
from apps.shared.models import BaseTimeModel


class EthnicityCount(BaseTimeModel):
    population = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    ethnicity = models.ForeignKey(Ethnicity, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)