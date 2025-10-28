from apps.citizens.ethnicities.models import Ethnicity
from apps.citizens.ethnicities.serializers import EthnicitySerializer
from apps.dictionary.views.base_model_view_set import BaseModelViewSet


class EthnicityViewSet(BaseModelViewSet):
    model = Ethnicity
    serializer_class = EthnicitySerializer