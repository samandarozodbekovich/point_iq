from apps.areas.places.models import Place
from apps.areas.places.serializers import PlaceSerializer
from apps.dictionary.views import BaseModelViewSet


class PlaceViewSet(BaseModelViewSet):
    model = Place
    serializer_class = PlaceSerializer
