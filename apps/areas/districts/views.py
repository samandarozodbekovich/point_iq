from apps.areas.districts.models import District
from apps.areas.districts.serializers import DistrictSerializer
from apps.core.views import BaseBulkMethods
from apps.shared.views.base_view_set import BaseModelViewSet


class DistrictViewSet(BaseBulkMethods, BaseModelViewSet):
    model = District
    serializer_class = DistrictSerializer

