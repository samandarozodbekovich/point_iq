from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hitcount.models import HitCount

from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.shared.models import BaseNameModel, BaseTimeModel



class Competitor(BaseNameModel, BaseTimeModel):
    category = models.ForeignKey(CompetitorCategory, on_delete=models.CASCADE)
    address = models.CharField(max_length=120)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    # Analytics fields
    average_rating = models.FloatField(null=True, blank=True)
    footfall_estimate = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)

    # Hitcount
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                       related_query_name='competitor')


    def __str__(self):
        return self.name_uz or self.name_ru or self.name_uz_cyr or "Unnamed competitor"


    @property
    def all_comments(self):
        return self.reviews.all()


