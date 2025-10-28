from django.contrib import admin

from apps.areas.districts.models import District

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'city')
    search_fields = ('name_uz',)
    list_filter = ('city',)