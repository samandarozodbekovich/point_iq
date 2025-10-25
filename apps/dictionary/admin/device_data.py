from django.contrib import admin

from apps.dictionary.devices.device_data.models import DeviceData


@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'home_location')
    list_filter = ('home_location',)
    ordering = ('-created_at',)