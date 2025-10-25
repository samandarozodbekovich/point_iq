from django.contrib import admin

from apps.dictionary.devices.footfall_event.models import FootfallEvent


@admin.register(FootfallEvent)
class FootfallEventAdmin(admin.ModelAdmin):
    list_display = ('id','device', 'location', 'timestamp', 'dwell_time_minutes')
    list_filter = ('device',)
    ordering = ('-timestamp',)
    search_fields = ('device',)
