from django.contrib import admin

from apps.competitors.admin.competitor_review import CompetitorReviewInline
from apps.competitors.competitor.models import Competitor


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_uz','category', 'address', 'latitude',"longitude")
    list_filter = ('category', )
    search_fields = ('category', 'address')
    ordering = ('category',)
    inlines = [CompetitorReviewInline]


