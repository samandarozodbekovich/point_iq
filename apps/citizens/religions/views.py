from apps.citizens.religions.models import Religion
from apps.citizens.religions.serializers import ReligionSerializer
from apps.dictionary.views import BaseModelViewSet


class ReligionViewSet(BaseModelViewSet):
    model = Religion
    serializer_class = ReligionSerializer