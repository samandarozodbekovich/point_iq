from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hitcount.models import HitCount

from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.shared.models import BaseNameModel, BaseTimeModel



class Competitor(BaseNameModel, BaseTimeModel):
    category = models.ForeignKey(CompetitorCategory, on_delete=models.SET_NULL , null=True, blank=True)
    address = models.CharField(max_length=120)
    external_id = models.BigIntegerField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    schedule_from=models.CharField(max_length=50, null=True, blank=True)
    schedule_to=models.CharField(max_length=50, null=True, blank=True)

    average_rating = models.FloatField(null=True, blank=True)
    footfall_estimate = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)

    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                       related_query_name='competitor')


    def __str__(self):
        return self.name_uz or self.name_ru or self.name_cyr or "Unnamed competitor"


    @property
    def all_comments(self):
        return self.reviews.all()


