from apps.dictionary.views.base_model_view_set import BaseModelViewSet
from apps.areas.areas.models import Area
from apps.areas.areas.serializers import AreaSerializer


class AreaViewSet(BaseModelViewSet):
    model = Area
    serializer_class = AreaSerializer



