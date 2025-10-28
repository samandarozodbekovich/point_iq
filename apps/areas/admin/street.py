from django.contrib import admin

from apps.areas.streets.models import Street

@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    list_display = ('name_uz','area')
    search_fields = ('name_uz',)
    list_filter = ('area',)