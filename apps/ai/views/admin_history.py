from rest_framework.mixins import ListModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer


class AdminHistoryViewSet(GenericViewSet, ListModelMixin, DestroyModelMixin):

    permission_classes = [IsAdminUser]
    serializer_class = QueryHistorySerializer
    queryset = QueryHistory.objects.all().order_by("-created_at", "-id")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "deleted query"},
            status=status.HTTP_204_NO_CONTENT
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search by user_query
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(user_query__icontains=search)

        # Filter by region
        region = request.query_params.get('region')
        if region:
            queryset = queryset.filter(region__icontains=region)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)