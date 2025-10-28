from apps.citizens.population_statistic.serializers import PopulationStatisticSerializer
from apps.dictionary.views import BaseModelViewSet
from apps.citizens.population_statistic.models import PopulationStatistic


class PopulationStatisticViewSet(BaseModelViewSet):
    model = PopulationStatistic
    serializer_class = PopulationStatisticSerializer