from django.contrib import admin
from apps.property.property_listing.models import PropertyListing


@admin.register(PropertyListing)
class PropertyListingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'owner','title', 'address',
        'is_for_sale', 'is_for_rent', 'is_deleted'
    )

    search_fields = ('title', 'description', 'property_type')
    list_filter = ('property_type', 'currency', 'is_for_sale', 'is_for_rent', 'year_built', 'created_at', 'is_deleted')
    ordering = ('-created_at','is_deleted')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # faqat yangi yozuvda
            obj.owner = request.user
        obj.save()

    def get_queryset(self, request):
        return PropertyListing.all_objects.all()
