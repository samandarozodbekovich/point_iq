from django.contrib import admin

from apps.property.property_feature.models import PropertyFeature


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ('property', 'feature_value', 'created_at')
    list_filter = ('property', 'feature_value')
    search_fields = ('property', 'feature_value')
    ordering = ('-created_at',)

    list_select_related = ('property', )



