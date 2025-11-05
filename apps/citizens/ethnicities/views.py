from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.citizens.ethnicities.models import Ethnicity, EthnicityPopulation
from apps.citizens.ethnicities.serializers import EthnicitySerializer, EthnicityPopulationSerializer


class EthnicityAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = EthnicitySerializer
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return Ethnicity.objects.filter(pk=pk)
        return Ethnicity.objects.all()


class EthnicityPopulationAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = EthnicityPopulationSerializer
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return EthnicityPopulation.objects.filter(pk=pk)
        return EthnicityPopulation.objects.all()
