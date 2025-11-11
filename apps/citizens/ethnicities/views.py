
from apps.citizens.ethnicities.models import Ethnicity, EthnicityPopulation
from apps.citizens.ethnicities.serializers import EthnicitySerializer, EthnicityPopulationSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class EthnicityViewSet(BaseModelViewSet):
    model = Ethnicity
    serializer_class = EthnicitySerializer



class EthnicityPopulationViewSet(BaseModelViewSet):
    model = EthnicityPopulation
    serializer_class = EthnicityPopulationSerializer

