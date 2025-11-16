from django.urls import path,include
from rest_framework.routers import DefaultRouter

from apps.citizens.age_groups.views import AgeGroupViewSet, AgeGroupPopulationViewSet
from apps.citizens.population.views import PopulationViewSet
from apps.citizens.relationship_status.views import RelationshipStatusViewSet, RelationshipStatusPopulationViewSet

router = DefaultRouter()
router.register('age-groups', AgeGroupViewSet, basename='age-groups')
router.register('population', PopulationViewSet, basename='population')
router.register('relationship-status', RelationshipStatusViewSet, basename='relationship-status')
router.register('relationship-status-population', RelationshipStatusPopulationViewSet, basename='relationship-status-population')
router.register('age_group-population', AgeGroupPopulationViewSet, basename='age-group-population')

urlpatterns = [
    path('',include(router.urls)),
]