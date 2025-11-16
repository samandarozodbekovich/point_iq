from django.contrib import admin

from apps.areas.districts.models import District

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id','name_uz','name_ru','name_uz_cyr', 'city')
    search_fields = ('name_uz','name_ru','name_uz_cyr')
    list_filter = ('city',)