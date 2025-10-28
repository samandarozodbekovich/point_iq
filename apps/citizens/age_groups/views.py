from rest_framework import viewsets, permissions

from apps.citizens.age_groups.models import AgeGroup
from apps.citizens.age_groups.serializers import AgeGroupSerializer


class AgeGroupViewSet(viewsets.ModelViewSet):
    serializer_class = AgeGroupSerializer
    queryset = AgeGroup.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return AgeGroup.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return AgeGroup.objects.filter(id = self.kwargs['pk'])
        else:
            return AgeGroup.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny,]
        elif self.action in ['update', 'partial_update', 'create']:
            return [permissions.IsAdminUser,]

