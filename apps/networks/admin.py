from django.contrib import admin

from .models import CellTower


@admin.register(CellTower)
class CellTowerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "latitude",
        "longitude",
        "radio",
        "mcc",
        "mnc",
        "lac",
        "cellid",
        "range_meters",
        "samples",
        "changeable",
        "created_at",
    )
    list_filter = ("radio", "mcc", "mnc", "changeable")
    search_fields = ("latitude", "longitude", "cellid")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

