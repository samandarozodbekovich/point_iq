from apps.core.serializers.base_bulk import BaseBulkSerializer
from apps.core.serializers.base_bulk_list import BaseBulkListSerializer
from apps.property.property_images.models import PropertyImage


# BaseBulkSerializer is the per-item base class; the list class goes in
# Meta.list_serializer_class. It used to be set the other way round, so
# every many=True call (list, bulk create/update) failed with a TypeError.
class PropertyImageSerializer(BaseBulkSerializer):

    class Meta:
        model = PropertyImage
        fields = [
            'id',
            'property',
            'image',
        ]
        list_serializer_class = BaseBulkListSerializer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # PropertyListing has no name_uz; its display name is title.
        data['property'] = instance.property.title if instance.property else None
        return data
