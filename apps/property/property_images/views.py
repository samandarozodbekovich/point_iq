from apps.core.views import BaseBulkMethods
from apps.property.property_images.models import PropertyImage
from apps.property.property_images.serializers import PropertyImageSerializer
from apps.shared.views.base_deleted_items_view_set import BaseDeletedItemsViewSet


class PropertyImageViewSet(BaseBulkMethods, BaseDeletedItemsViewSet):
    model = PropertyImage
    serializer_class = PropertyImageSerializer

