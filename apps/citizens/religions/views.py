
from apps.citizens.religions.models import Religion, ReligionCount
from apps.citizens.religions.serializers import ReligionSerializer, ReligionCountSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class ReligionViewSet(BaseModelViewSet):
    model = Religion
    serializer_class = ReligionSerializer



class ReligionCountViewSet(BaseModelViewSet):
    model = ReligionCount
    serializer_class = ReligionCountSerializer

