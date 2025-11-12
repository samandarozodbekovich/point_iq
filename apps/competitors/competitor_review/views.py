from rest_framework import viewsets, permissions

from apps.competitors.competitor_review.models import CompetitorReview
from apps.competitors.competitor_review.serializers import CompetitorReviewSerializer


class CompetitorReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CompetitorReviewSerializer
    queryset = CompetitorReview.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['destroy', 'partial_update', 'update']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)