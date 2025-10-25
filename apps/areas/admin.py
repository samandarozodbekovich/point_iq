from django.contrib import admin
from apps.areas.cities.models import City
from apps.areas.districts.models import District
from apps.areas.areas.models import Area
from apps.areas.streets.models import Street
from apps.areas.places.models import Place

# Register your models here.

class CityAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)
    search_fields = ('name_uz',)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'city')
    search_fields = ('name_uz',)
    list_filter = ('city',)


class AreaAdmin(admin.ModelAdmin):
    list_display = ('name_uz','district')
    search_fields = ('name_uz',)
    list_filter = ('district',)


class StreetAdmin(admin.ModelAdmin):
    list_display = ('name_uz','area')
    search_fields = ('name_uz',)
    list_filter = ('area',)


class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('name_uz','street', 'category')
    search_fields = ('name_uz',)
    list_filter = ('category',)
    ordering = ('rating',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz',)


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('house_number','street')
    search_fields = ('house_number',)
    list_filter = ('street',)


admin.site.register(City, CityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(Place, PlaceAdmin)


