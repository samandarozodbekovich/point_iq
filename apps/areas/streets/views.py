from apps.areas.streets.models import Street
from apps.areas.streets.serializers import StreetSerializer
from apps.dictionary.views import BaseModelViewSet


class StreetViewSet(BaseModelViewSet):
    model = Street
    serializer_class = StreetSerializer
