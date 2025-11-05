from apps.areas.places.models import Place
from apps.areas.places.serializers import PlaceSerializer
from apps.core.views import BaseBulkMethods
from apps.shared.views.base_view_set import BaseModelViewSet


class PlaceViewSet(BaseBulkMethods, BaseModelViewSet):
    model = Place
    serializer_class = PlaceSerializer
