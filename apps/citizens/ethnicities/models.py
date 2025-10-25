from django.db import models

from apps.citizens.population.models import Citizen
from apps.shared.models import BaseNameModel, BaseTimeModel


class Ethnicity(BaseNameModel, BaseTimeModel):

    def __str__(self):
        return self.name_uz
