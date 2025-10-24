from django.db import models

from apps.competitors.competitor.models import Competitor
from apps.shared.models import BaseTimeModel


class CompetitorAnalytics(BaseTimeModel):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='analytics')
    date_recorded = models.DateField()
    footfall_estimate = models.IntegerField()
    average_rating = models.DecimalField(max_digits=3, decimal_places=1)
    review_count = models.IntegerField()