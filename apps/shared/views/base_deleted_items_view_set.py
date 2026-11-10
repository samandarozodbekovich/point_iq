from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ..permissions import IsOwnerOrAdmin


class BaseDeletedItemsViewSet(viewsets.ModelViewSet):
    model = None
    serializer_class = None
    # Anonymous users may read; creating needs an account (the object gets an
    # owner); changing an object needs to be its owner or staff.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]

    # Write actions that touch many objects at once. has_object_permission
    # never runs for them, so ownership can't be checked: admin only.
    LIST_WRITE_ACTIONS = ('bulk_create', 'bulk_update')

    def get_permissions(self):
        if self.action in self.LIST_WRITE_ACTIONS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_owner_id(self, obj):
        return obj.owner_id

    def get_queryset(self):
        return self.model.objects.filter(is_deleted=False).order_by("-created_at")

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






