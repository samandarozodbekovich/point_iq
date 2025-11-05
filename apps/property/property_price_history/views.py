
from apps.property.property_price_history.models import PropertyPriceHistory
from apps.property.property_price_history.serializers import PropertyPriceHistorySerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class PropertyPriceHistoryViewSet(BaseModelViewSet):
    model = PropertyPriceHistory
    serializer_class = PropertyPriceHistorySerializer