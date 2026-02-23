from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from apps.competitors.admin.competitor_review import CompetitorReviewInline
from apps.competitors.competitor.models import Competitor


@admin.register(Competitor)
class CompetitorAdmin(LeafletGeoAdmin):  # OSMGeoAdmin o'rniga LeafletGeoAdmin
    list_display = ('id', 'name_uz', 'category', 'address', 'latitude', 'longitude')
    list_filter = ('category',)
    search_fields = ('name_uz', 'category', 'address')  # name_uz ni ham qo'shdik
    ordering = ('category',)
    inlines = [CompetitorReviewInline]

    # Xarita maydoni admin panelda kengroq ko'rinishi uchun
    settings_overrides = {
        'DEFAULT_CENTER': (41.311081, 69.240562),
    }