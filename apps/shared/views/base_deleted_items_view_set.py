from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ..permissions import IsOwnerOrAdmin


class BaseDeletedItemsViewSet(viewsets.ModelViewSet):
    model = None
    serializer_class = None
    permission_classes = [permissions.AllowAny, IsOwnerOrAdmin]

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs.get("pk")).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)

    # For admin
    @action(detail=False, methods=['get'], url_path="admin-list")
    def admin_list(self, request):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        place = self.model.all_objects.all()
        serializer = self.get_serializer(place, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['post'], url_path="restore")
    def restore(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        place = get_object_or_404(self.model.all_objects, pk=pk)
        place.restore()
        return Response(self.get_serializer(place).data)


    @action(detail=False, methods=['delete'], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
        place = get_object_or_404(self.model.all_objects, pk=pk)
        place.hard_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






