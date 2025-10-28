from django.urls import path,include

from rest_framework.routers import DefaultRouter

from apps.competitors.competitor.views import CompetitorViewSet
from apps.competitors.competitor_categories.views import CompetitorCategoryViewSet
from apps.competitors.competitor_analytics.views import CompetitorAnalyticsViewSet


router = DefaultRouter()
router.register(r'', CompetitorViewSet, basename='competitors')
router.register(r'category', CompetitorCategoryViewSet, basename='competitor_category')
router.register(r'analytics', CompetitorAnalyticsViewSet, basename='competitor_analytics')


urlpatterns = [
    path('', include(router.urls)),
]