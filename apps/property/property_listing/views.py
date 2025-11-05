from apps.core.views import BaseBulkMethods
from apps.property.property_listing.models import PropertyListing
from apps.property.property_listing.serializers import PropertyListingSerializer
from apps.shared.views.base_deleted_items_view_set import BaseDeletedItemsViewSet


class PropertyListingViewSet(BaseBulkMethods, BaseDeletedItemsViewSet ):
    model = PropertyListing
    serializer_class = PropertyListingSerializer