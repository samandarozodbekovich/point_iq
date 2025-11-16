from django.contrib import admin

from apps.dictionary.cars.car_traffic.models import CarTraffic


@admin.register(CarTraffic)
class CarTrafficAdmin(admin.ModelAdmin):
    list_display = ('district','date_recorded', 'average_daily_cars', 'peak_hour', 'congestion_level', 'source')
    list_filter = ('district','date_recorded','peak_hour','congestion_level')
    ordering = ('district', 'date_recorded')
    search_fields = ('district', 'date_recorded')
    list_per_page = 50

