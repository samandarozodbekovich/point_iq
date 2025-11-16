from django.contrib import admin
from apps.dictionary.crimes.crime_statistics.models import CrimeStatistics


@admin.register(CrimeStatistics)
class CrimeStatisticsAdmin(admin.ModelAdmin):
    list_display = ('crime', 'district', 'rating')
    list_filter = ('crime',)
    ordering = ('-created_at','rating')