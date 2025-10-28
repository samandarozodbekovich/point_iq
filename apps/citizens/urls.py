from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.citizens.age_groups.views import AgeGroupViewSet

router = DefaultRouter()
router.register('age-groups', AgeGroupViewSet, basename='age-groups')


urlpatterns = [
    path('', include(router.urls)),
]