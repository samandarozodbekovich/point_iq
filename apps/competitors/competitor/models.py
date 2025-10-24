from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.competitors.competitor_categories.models import Category
from apps.areas.places.models import Place
from apps.shared.models import BaseNameModel, BaseTimeModel



class Competitor(BaseNameModel, BaseTimeModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    ,null=True,blank=True)

    def __str__(self):
        return f"{self.name_uz} at {self.place}"

