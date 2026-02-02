from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import QueryHistory
from ..serializers import QueryHistorySerializer

class UserHistoryView(ListAPIView, RetrieveAPIView):

    permission_classes = [IsAuthenticated,]
    serializer_class = QueryHistorySerializer
    queryset = QueryHistory.objects.all().order_by("-created_at")

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return QueryHistory.objects.none()  # response empty queryset
        return QueryHistory.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        history = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer(history)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)