from django.contrib import admin

from apps.citizens.population_statistic.models import PopulationStatistic


@admin.register(PopulationStatistic)
class PopulationStatisticAdmin(admin.ModelAdmin):
    list_display = ('population', 'age_group','population_count')
    list_filter = ('population',)
    list_per_page = 50