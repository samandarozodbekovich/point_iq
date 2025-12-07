from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.competitors.competitor.models import Competitor
from apps.users.models import User


class CompetitorReview(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.SET_NULL , null=True, blank=True, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    comment = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.first_name} support the {self.competitor.name_uz}"

