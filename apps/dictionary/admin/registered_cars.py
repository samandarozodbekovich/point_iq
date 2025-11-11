from django.contrib import admin

from apps.dictionary.cars.registered_cars.models import RegisteredCar


@admin.register(RegisteredCar)
class RegisteredCarAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'car_type', 'year', 'month', 'registered_count', 'source')
    ordering = ('-registered_count',)
    search_fields = ('address',)
    list_filter = ('address', 'car_type', 'year', 'month')