from rest_framework import viewsets, permissions

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

        if getattr(self, 'swagger_fake_view', False):
            return CompetitorReview.objects.none()

        competitor_id = self.kwargs['competitor_pk']

        if competitor_id is None:
            return CompetitorReview.objects.none()

        return CompetitorReview.objects.filter(competitor_id=competitor_id)

    def perform_create(self, serializer):
        competitor_id = self.kwargs['competitor_pk']
        serializer.save(user=self.request.user, competitor_id=competitor_id)