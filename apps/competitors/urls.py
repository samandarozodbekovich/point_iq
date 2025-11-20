from django.urls import path,include

from rest_framework_nested import routers

from rest_framework.routers import DefaultRouter

from apps.competitors.competitor.views import CompetitorViewSet
from apps.competitors.competitor_categories.views import CompetitorCategoryViewSet
from apps.competitors.competitor_review.views import CompetitorReviewViewSet


router = DefaultRouter()
router.register(r'competitor', CompetitorViewSet,  basename='competitors')
router.register(r'category', CompetitorCategoryViewSet, basename='competitor-category')

competitor_router = routers.NestedDefaultRouter(router, r'competitor', lookup='competitor')
competitor_router.register(r'reviews', CompetitorReviewViewSet, basename='competitor-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(competitor_router.urls)),
]
