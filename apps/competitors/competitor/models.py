from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as geo_models
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hitcount.models import HitCount

from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.shared.models import BaseNameModel, BaseTimeModel



def point_from(latitude, longitude):
    if latitude is None or longitude is None:
        return None
    return Point(float(longitude), float(latitude), srid=4326)


class CompetitorQuerySet(models.QuerySet):
    """Keeps `location` in step with latitude/longitude on bulk writes.

    bulk_create/bulk_update skip save(), so every bulk caller had to build
    the Point itself (2GIS did, anything new could forget). Doing it here
    makes latitude/longitude the single source of truth.
    """

    def bulk_create(self, objs, *args, **kwargs):
        objs = list(objs)
        for obj in objs:
            obj.sync_location()
        return super().bulk_create(objs, *args, **kwargs)

    def bulk_update(self, objs, fields, *args, **kwargs):
        objs, fields = list(objs), list(fields)
        if {'latitude', 'longitude'} & set(fields):
            for obj in objs:
                obj.sync_location()
            if 'location' not in fields:
                fields.append('location')
        return super().bulk_update(objs, fields, *args, **kwargs)

    def update(self, **kwargs):
        if ('latitude' in kwargs or 'longitude' in kwargs) and 'location' not in kwargs:
            # Only computable when both are plain values for every row.
            if 'latitude' not in kwargs or 'longitude' not in kwargs or \
                    hasattr(kwargs['latitude'], 'resolve_expression') or \
                    hasattr(kwargs['longitude'], 'resolve_expression'):
                raise ValueError("Update latitude and longitude together (as values) so location stays in sync.")
            kwargs['location'] = point_from(kwargs['latitude'], kwargs['longitude'])
        return super().update(**kwargs)


class Competitor(BaseNameModel, BaseTimeModel):
    category = models.ForeignKey(CompetitorCategory, on_delete=models.SET_NULL , null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    external_id = models.TextField(null=True, blank=True, unique=True)
    google_place_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)

    location = geo_models.PointField(srid=4326, null=True, blank=True)

    schedule_from=models.CharField(max_length=50, null=True, blank=True)
    schedule_to=models.CharField(max_length=50, null=True, blank=True)

    average_rating = models.FloatField(null=True, blank=True)
    footfall_estimate = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)

    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                       related_query_name='competitor')

    objects = CompetitorQuerySet.as_manager()

    def __str__(self):
        return self.name_uz or self.name_ru or self.name_cyr or "Unnamed competitor"

    @property
    def all_comments(self):
        return self.reviews.all()

    def sync_location(self):
        # Also clears location when coordinates are removed; save() used to
        # leave the old point behind in that case.
        self.location = point_from(self.latitude, self.longitude)

    def save(self, *args, **kwargs):
        self.sync_location()
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and {'latitude', 'longitude'} & set(update_fields):
            kwargs['update_fields'] = set(update_fields) | {'location'}
        super().save(*args, **kwargs)


