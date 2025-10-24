from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from apps.areas.areas.models import Area
from apps.areas.areas.serializers import AreaSerializer


class AreaViewset(ModelViewSet):
    serializer_class = AreaSerializer
    queryset = Area.objects.all()

    if action in ['list', 'retrieve']:
        permission_classes = (permissions.AllowAny,)
    else:
        permission_classes = (permissions.IsAdminUser,)


