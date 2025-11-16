from django.contrib import admin

from apps.citizens.population.models import Population


@admin.register(Population)
class PopulationAdmin(admin.ModelAdmin):
    list_display = ('id','district', 'count_male', 'count_female', 'average_income','population_density')
    search_fields = ('district',)
    list_filter = ('district',)
    list_per_page = 50