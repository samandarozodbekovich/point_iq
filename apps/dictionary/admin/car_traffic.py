from django.contrib import admin

from apps.dictionary.cars.car_traffic.models import CarTraffic


@admin.register(CarTraffic)
class CarTrafficAdmin(admin.ModelAdmin):
    list_display = ('area', 'street', 'date_recorded', 'average_daily_cars', 'peak_hour', 'congestion_level', 'source')
    list_filter = ('area','street','date_recorded','peak_hour','congestion_level')
    ordering = ('area', 'street', 'date_recorded')
    search_fields = ('area', 'street', 'date_recorded')
    list_per_page = 50

