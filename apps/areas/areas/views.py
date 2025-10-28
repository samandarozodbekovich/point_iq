from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.areas.areas.models import Area
from apps.areas.areas.serializers import AreaSerializer


class AreaViewSet(ModelViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all()

    def get_queryset(self):
        if self.action in ['list', 'create']:
            return Area.objects.all()
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return Area.objects.filter(id=self.kwargs['pk'])
        return Area.objects.none()

    def get_permissions(self):

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


