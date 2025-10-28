from apps.citizens.ethnicity_count.models import EthnicityCount
from apps.citizens.ethnicity_count.serializers import EthnicityCountSerializer
from apps.dictionary.views import BaseModelViewSet


class EthnicityCountViewSet(BaseModelViewSet):
    model = EthnicityCount
    serializer_class = EthnicityCountSerializer