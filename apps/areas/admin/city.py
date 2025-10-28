from django.contrib import admin

from apps.areas.cities.models import City

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    search_fields = ('name_uz',)