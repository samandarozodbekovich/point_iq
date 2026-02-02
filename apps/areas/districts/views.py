from apps.areas.districts.models import District
from apps.areas.districts.serializers import DistrictSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class DistrictViewSet(BaseModelViewSet):
    model = District
    serializer_class = DistrictSerializer

