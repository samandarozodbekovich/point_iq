from apps.areas.address.models import Address
from apps.areas.address.serializers import AddressSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class AddressViewSet(BaseModelViewSet):
    model = Address
    serializer_class = AddressSerializer
