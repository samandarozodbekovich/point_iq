from django.contrib import admin

from apps.citizens.age_groups.models import AgeGroup, AgeGroupPopulation


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('id','age_group',)
    list_per_page = 50



@admin.register(AgeGroupPopulation)
class AgeGroupPopulationAdmin(admin.ModelAdmin):
    list_display = ('id','population','age_group','count')
    list_per_page = 50