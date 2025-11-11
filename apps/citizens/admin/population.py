from django.contrib import admin

from apps.citizens.population.models import Population


@admin.register(Population)
class PopulationAdmin(admin.ModelAdmin):
    list_display = ('district', 'count_male', 'count_female', 'average_income', 'unemployment_rate')
    search_fields = ('district',)
    list_filter = ('district',)
    list_per_page = 50