from django.contrib import admin

from apps.property.property_images.models import PropertyImage


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property__owner', 'image', 'is_deleted')
    list_filter = ('property','is_deleted')
    ordering = ('-created_at','is_deleted')

    list_select_related = ('property', )

    def get_queryset(self, request):
        return PropertyImage.all_objects.all()