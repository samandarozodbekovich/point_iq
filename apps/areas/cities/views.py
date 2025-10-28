from apps.dictionary.views.base_model_view_set import BaseModelViewSet
from apps.areas.cities.models import City
from apps.areas.cities.serializers import CitySerializer


class CityViewSet(BaseModelViewSet):
    model = City
    serializer_class = CitySerializer
