from django.urls import path,include

from rest_framework.routers import DefaultRouter

from apps.competitors.competitor.views import CompetitorViewSet
from apps.competitors.competitor_categories.views import CompetitorCategoryViewSet


router = DefaultRouter()
router.register('', CompetitorViewSet)
router.register('category', CompetitorCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]