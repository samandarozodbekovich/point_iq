from django.contrib import admin

from apps.areas.cities.models import City

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id','name_uz', 'name_ru', 'name_cyr')
    search_fields = ('name_uz', 'name_ru', 'name_cyr')
