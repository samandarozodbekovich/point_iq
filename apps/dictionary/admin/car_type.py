from django.contrib import admin

from apps.dictionary.cars.car_type.models import CarType


@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_cyr')
    search_fields = ('name_uz', 'name_ru', 'name_cyr')
    list_filter = ('name_uz', 'name_ru', 'name_cyr')
    ordering = ('-created_at',)
