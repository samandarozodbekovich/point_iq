from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin
from apps.dictionary.population_traffic.models.traffic_note import TrafficNoteModel

@admin.register(TrafficNoteModel)
class TrafficNoteAdmin(LeafletGeoAdmin):
    display_raw = True

    list_display = ('name', 'location', 'node_type', 'base_weight', 'manual_flow_estimate')
    list_filter = ['location', 'node_type', 'base_weight', 'manual_flow_estimate']
    search_fields = ['name', 'location', 'node_type', 'base_weight', 'manual_flow_estimate']
    ordering = ('-created_at',)

    default_lon = 69.2401
    default_lat = 41.2995
    default_zoom = 12