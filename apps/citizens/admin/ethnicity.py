from django.contrib import admin

from apps.citizens.ethnicities.models import Ethnicity,EthnicityPopulation


@admin.register(Ethnicity)
class EthnicityAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)



@admin.register(EthnicityPopulation)
class EthnicityPopulationAdmin(admin.ModelAdmin):
    list_display = ('population','ethnicity','count')
    list_filter = ('population','ethnicity')
    list_per_page = 50