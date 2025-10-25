from django.contrib import admin

from apps.property.property_price_history.models import PropertyPriceHistory


@admin.register(PropertyPriceHistory)
class PropertyPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('property', 'date_recorded', 'price', 'currency', 'source')
    list_filter = ('property',)
    ordering = ('-date_recorded','price')

    list_select_related = ('property', )

