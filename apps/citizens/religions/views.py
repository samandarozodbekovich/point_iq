from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.citizens.religions.models import Religion, ReligionCount
from apps.citizens.religions.serializers import ReligionSerializer, ReligionCountSerializer


class ReligionAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = ReligionSerializer
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return Religion.objects.filter(pk=pk)
        return Religion.objects.all()


class ReligionCountAPIView(ListAPIView, RetrieveAPIView):
    serializer_class = ReligionCountSerializer
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return ReligionCount.objects.filter(pk=pk)
        return ReligionCount.objects.all()
