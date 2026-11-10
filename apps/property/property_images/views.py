from rest_framework.exceptions import PermissionDenied

from apps.core.views import BaseBulkMethods
from apps.property.property_images.models import PropertyImage
from apps.property.property_images.serializers import PropertyImageSerializer
from apps.shared.views.base_deleted_items_view_set import BaseDeletedItemsViewSet


class PropertyImageViewSet(BaseBulkMethods, BaseDeletedItemsViewSet):
    model = PropertyImage
    serializer_class = PropertyImageSerializer

    # Images have no owner field; they belong to whoever owns the listing.
    def get_owner_id(self, obj):
        return obj.property.owner_id if obj.property_id else None

    def _check_listing_owner(self, serializer):
        listing = serializer.validated_data.get('property')
        user = self.request.user
        if listing is not None and not user.is_staff and listing.owner_id != user.id:
            raise PermissionDenied("You can only add images to your own listings.")

    def perform_create(self, serializer):
        # The base class saves owner=..., but PropertyImage has no owner field.
        self._check_listing_owner(serializer)
        serializer.save()

    def perform_update(self, serializer):
        # Stops moving an image onto someone else's listing.
        self._check_listing_owner(serializer)
        serializer.save()
