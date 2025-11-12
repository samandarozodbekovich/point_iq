from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from apps.competitors.competitor_review.models import CompetitorReview
from apps.competitors.competitor_review.serializers import CompetitorReviewSerializer


class CompetitorReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CompetitorReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['destroy', 'partial_update', 'update']:
            return [permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]


    def get_queryset(self):
        competitor_id = self.kwargs['competitor_pk']  # nested router bilan keladi
        return CompetitorReview.objects.filter(competitor_id=competitor_id)

    def perform_create(self, serializer):
        competitor_id = self.kwargs['competitor_pk']
        serializer.save(user=self.request.user, competitor_id=competitor_id)