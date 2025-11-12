from django.urls import path,include

from rest_framework.routers import DefaultRouter

from apps.competitors.competitor.views import CompetitorViewSet
from apps.competitors.competitor_categories.views import CompetitorCategoryViewSet
from apps.competitors.competitor_review.views import CompetitorReviewViewSet


router = DefaultRouter()
router.register('', CompetitorViewSet,  basename='competitors')
router.register('category', CompetitorCategoryViewSet, basename='competitor-category')
router.register('reviews', CompetitorReviewViewSet, basename='competitor-reviews')

urlpatterns = [
    path('', include(router.urls)),
]