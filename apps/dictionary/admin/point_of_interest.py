from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin

from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel


@admin.register(PointOfInterestModel)
class PointOfInterestModelAdmin(LeafletGeoAdmin):
    display_raw = True

    list_display = ['id', 'name', 'category', 'location']
    list_filter = ['category', 'influence_radius', 'attraction_factor']
    search_fields = ['name', 'category', 'location', 'influence_radius', 'attraction_factor']
    ordering = ('category', 'location', 'influence_radius', 'attraction_factor', '-created_at')
