from django.contrib import admin

from apps.areas.places.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("id", "street", "house_number", "latitude", "longitude", "description", "created_at")
    list_filter = ("street",)
    search_fields = ("street__name", "house_number", "description")
    ordering = ("id",)