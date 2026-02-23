
from rest_framework import serializers
from django.contrib.gis.geos import Point


class TrafficRequestSerializer(serializers.Serializer):
    long = serializers.FloatField()
    lat = serializers.FloatField()
    radius = serializers.IntegerField(default=500, min_value=100, max_value=2000)

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        internal_data["point"] = Point(internal_data['long'],internal_data['lat'], srid=4326)
        return internal_data

