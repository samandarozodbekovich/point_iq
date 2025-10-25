from django.contrib import admin
from apps.competitors.competitor.models import Competitor


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'place', 'rating')
    list_filter = ('category', )
    search_fields = ('category', 'place')
    ordering = ('category', 'rating')

