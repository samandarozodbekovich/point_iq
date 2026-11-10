import json
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Area
from django.contrib.gis.geos import Point
from django.db import models

from apps.areas.cities.models import City
from apps.shared.models import BaseNameModel, BaseTimeModel




class District(BaseNameModel, BaseTimeModel):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    # Legacy: the first outer ring as a list of [lon, lat]. Kept for
    # reference; lookups use `boundary`.
    boundary_json = models.JSONField(null=True, blank=True, help_text="Polygon coordinates as JSON")
    # Full geometry (every part of a MultiPolygon) with a spatial index, so
    # "which district contains this point" is a single indexed query.
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)


    def __str__(self):
        return f"{self.name_uz} ({self.city.name_uz if self.city else 'no city'})"

    def get_boundary_coord(self):

        if not self.boundary_json:
            return None
        if isinstance(self.boundary_json, str):
            try:
                return json.loads(self.boundary_json)
            except json.JSONDecodeError:
                return None
        return self.boundary_json

    def is_point_inside(self, latitude, longitude):
        if self.boundary is None:
            return False
        try:
            return self.boundary.contains(Point(float(longitude), float(latitude), srid=4326))
        except (ValueError, TypeError):
            return False

    @classmethod
    def find_containing(cls, latitude, longitude):
        """The district containing the point, or None.

        Smallest area first: the whole-city boundary is loaded as a district
        too, and a point inside a real district is inside the city as well.
        """
        try:
            point = Point(float(longitude), float(latitude), srid=4326)
        except (ValueError, TypeError):
            return None
        return (cls.objects.filter(boundary__contains=point)
                .annotate(area=Area('boundary')).order_by('area').first())
