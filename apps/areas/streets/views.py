from apps.areas.streets.models import Street
from apps.areas.streets.serializers import StreetSerializer
from apps.core.views import BaseBulkMethods
from apps.shared.views.base_view_set import BaseModelViewSet


class StreetViewSet(BaseBulkMethods, BaseModelViewSet):
    model = Street
    serializer_class = StreetSerializer
