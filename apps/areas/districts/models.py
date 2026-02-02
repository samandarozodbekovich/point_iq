import json
from django.db import models

from apps.areas.cities.models import City
from apps.shared.functions import point_in_polygon
from apps.shared.models import BaseNameModel, BaseTimeModel




class District(BaseNameModel, BaseTimeModel):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    boundary_json = models.JSONField(null=True, blank=True, help_text="Polygon coordinates as JSON")


    def __str__(self):
        return f"{self.name_uz} ({self.city.name_uz if self.city else 'Shahar yo\'q'})"

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

        coord = self.get_boundary_coord()
        if not coord:
            return False

        try:
            lat = float(latitude)
            lon = float(longitude)
            return point_in_polygon(lat, lon, coord)
        except (ValueError, TypeError):
            return False