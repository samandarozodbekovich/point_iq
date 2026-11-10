from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from apps.competitors.admin.competitor_review import CompetitorReviewInline
from apps.competitors.competitor.models import Competitor


@admin.register(Competitor)
class CompetitorAdmin(LeafletGeoAdmin):  # Leaflet map instead of OSMGeoAdmin
    list_display = ('id', 'name_uz', 'category', 'address', 'latitude', 'longitude')
    list_filter = ('category',)
    search_fields = ('name_uz', 'category', 'address')  # includes name_uz
    ordering = ('category',)
    inlines = [CompetitorReviewInline]

    # wider map widget in the admin
    settings_overrides = {
        'DEFAULT_CENTER': (41.311081, 69.240562),
    }