from apps.citizens.religion_counts.models import ReligionCount
from apps.citizens.religion_counts.serializers import ReligionCountSerializer
from apps.dictionary.views import BaseModelViewSet


class ReligionCountViewSet(BaseModelViewSet):
    model = ReligionCount
    serializer_class = ReligionCountSerializer