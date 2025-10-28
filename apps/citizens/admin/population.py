from django.contrib import admin

from apps.citizens.population.models import Population


@admin.register(Population)
class PopulationAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'count_male', 'count_female', 'average_income', 'unemployment_rate')
    search_fields = ('apartment',)
    list_filter = ('apartment',)
    list_per_page = 50