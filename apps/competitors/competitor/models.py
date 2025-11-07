from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.shared.models import BaseNameModel, BaseTimeModel



class Competitor(BaseNameModel, BaseTimeModel):
    category = models.ForeignKey(CompetitorCategory, on_delete=models.CASCADE)
    address = models.CharField(max_length=120)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    ,null=True,blank=True)

    # Analytics fields
    footfall_estimate = models.IntegerField(null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name_uz or self.name_ru or self.name_uz_cyr or "Unnamed competitor"


