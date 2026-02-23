
from rest_framework import serializers


class TrafficHeatmapSerializer(serializers.Serializer):
    lat = serializers.FloatField(source="location.y")
    long = serializers.FloatField(source="location.x")
    weight = serializers.FloatField(source="base_weight")