from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from apps.dictionary.population_traffic.models.traffic_segment import TrafficSegmentModel

@admin.register(TrafficSegmentModel)
class TrafficSegmentAdmin(LeafletGeoAdmin):
    list_display = ('street_name', 'intensity_level', 'zone_color')
    list_editable = ('intensity_level', 'zone_color')
    list_filter = ('intensity_level', 'zone_color')