from django.contrib import admin
from apps.dictionary.crimes.crime_types.models import CrimeTypes


@admin.register(CrimeTypes)
class CrimeTypesAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_cyr')
    list_filter = ('name_uz', 'name_ru', 'name_cyr')
    ordering = ('-created_at',)