from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.citizens.age_groups.models import AgeGroup, AgeGroupPopulation
from apps.citizens.age_groups.serializers import AgeGroupSerializer, AgeGroupPopulationSerializer
from apps.shared.views.base_view_set import BaseModelViewSet


class AgeGroupAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = AgeGroupSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return AgeGroup.objects.filter(pk=pk)
        return AgeGroup.objects.all()


class AgeGroupPopulationAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = AgeGroupPopulationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return AgeGroupPopulation.objects.filter(pk=pk)
        return AgeGroupPopulation.objects.all()
