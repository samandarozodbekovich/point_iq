from apps.areas.districts.models import District
from apps.areas.districts.serializers import DistrictSerializer
from apps.dictionary.views import BaseModelViewSet


class DistrictViewSet(BaseModelViewSet):
    model = District
    serializer_class = DistrictSerializer

