from django.contrib import admin

from apps.property.property_images.models import PropertyImage


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image')
    list_filter = ('property',)
    ordering = ('-created_at',)

    list_select_related = ('property', )
