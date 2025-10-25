from django.contrib import admin
from apps.property.property_listing.models import PropertyListing


@admin.register(PropertyListing)
class PropertyListingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'title',
        'property_type',
        'price',
        'currency',
        'area_sq_m',
        'rooms',
        'floor',
        'total_floors',
        'year_built',
        'is_for_sale',
        'is_for_rent',
        'source',
        'date_listed',
        'date_updated',
    )


    search_fields = (
        'title',
        'description',
        'property_type',
        'source',
        'place__street__name_uz',
        'street__name_uz',
        'area__name_uz',
    )


    list_filter = (
        'property_type',
        'currency',
        'is_for_sale',
        'is_for_rent',
        'year_built',
        'source',
        'date_listed',
    )


    ordering = ('-date_listed',)

    list_select_related = ('place', 'street', 'area')

    readonly_fields = ('date_listed', 'date_updated')


