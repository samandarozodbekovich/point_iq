from rest_framework.mixins import ListModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer


class AdminHistoryViewSet(GenericViewSet, ListModelMixin, DestroyModelMixin):
<<<<<<< HEAD
    """Admin uchun barcha so'rovlarni ko'rish va o'chirish"""
=======

>>>>>>> 7cb6155 (Initial clean commit)
    permission_classes = [IsAdminUser]
    serializer_class = QueryHistorySerializer
    queryset = QueryHistory.objects.all().order_by("-created_at")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
<<<<<<< HEAD
            {"detail": "Query o'chirildi"},
=======
            {"detail": "deleted query"},
>>>>>>> 7cb6155 (Initial clean commit)
            status=status.HTTP_204_NO_CONTENT
        )

    def list(self, request, *args, **kwargs):
<<<<<<< HEAD
        """Barcha querylar (filter, search qo'shilgan)"""
=======
>>>>>>> 7cb6155 (Initial clean commit)
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