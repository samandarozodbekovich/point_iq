from django.contrib import admin

from apps.dictionary.cars.registered_cars.models import RegisteredCar


@admin.register(RegisteredCar)
class RegisteredCarAdmin(admin.ModelAdmin):
    list_display = ('id', 'street', 'car_type', 'year', 'month', 'registered_count', 'source')
    ordering = ('-registered_count',)
    search_fields = ('street',)
    list_filter = ('street', 'car_type', 'year', 'month')