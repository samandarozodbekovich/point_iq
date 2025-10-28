from django.contrib import admin

from apps.areas.places.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('house_number','street')
    search_fields = ('house_number',)
    list_filter = ('street',)