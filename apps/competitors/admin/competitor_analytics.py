from django.contrib import admin

from apps.competitors.competitor_analytics.models import CompetitorAnalytics


@admin.register(CompetitorAnalytics)
class CompetitorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'competitor', 'date_recorded', 'footfall_estimate', 'average_rating', 'review_count')
    list_filter = ('competitor', 'date_recorded')
    ordering = ('competitor', 'average_rating')
    search_fields = ('competitor', 'average_rating')

