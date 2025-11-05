from apps.core.views import BaseBulkMethods
from apps.property.property_feature.models import PropertyFeature
from apps.property.property_feature.serializers import PropertyFeatureSerializer
from apps.shared.views.base_deleted_items_view_set import BaseDeletedItemsViewSet


class PropertyFeatureViewSet(BaseDeletedItemsViewSet ):
    model = PropertyFeature
    serializer_class = PropertyFeatureSerializer