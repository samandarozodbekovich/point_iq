from django.urls import path,include

from rest_framework.routers import DefaultRouter

from apps.competitors.competitor.views import CompetitorSearchAPIView
from apps.competitors.competitor_categories.views import CompetitorCategoryAPIView
from apps.competitors.competitor_analytics.views import CompetitorAnalyticsViewSet



router = DefaultRouter()

router.register(r'analytics', CompetitorAnalyticsViewSet, basename='competitor-analytics')


urlpatterns = [
    path('', include(router.urls)),
    path('search/', CompetitorSearchAPIView.as_view()),
    path('category/<str:category_name>/', CompetitorCategoryAPIView.as_view()),
]