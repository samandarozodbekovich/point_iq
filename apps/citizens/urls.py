from django.urls import path,include
from rest_framework.routers import DefaultRouter

from apps.citizens.age_groups.views import AgeGroupViewSet, AgeGroupPopulationViewSet
from apps.citizens.ethnicities.views import EthnicityViewSet, EthnicityPopulationViewSet
from apps.citizens.population.views import PopulationViewSet
from apps.citizens.relationship_status.views import RelationshipStatusViewSet, RelationshipStatusPopulationViewSet
from apps.citizens.religions.views import ReligionViewSet, ReligionCountViewSet

router = DefaultRouter()
router.register('religions', ReligionViewSet, basename='religions')
router.register('age-groups', AgeGroupViewSet, basename='age-groups')
router.register('population', PopulationViewSet, basename='population')
router.register('relationship-status', RelationshipStatusViewSet, basename='relationship-status')
router.register('relationship-status-population', RelationshipStatusPopulationViewSet, basename='relationship-status-population')
router.register('religion-count', ReligionCountViewSet, basename='religion-count')
router.register('age_group-population', AgeGroupPopulationViewSet, basename='age-group-population')
router.register('ethnicity', EthnicityViewSet, basename='ethnicity')
router.register('ethnicity-population', EthnicityPopulationViewSet, basename='ethnicity-population')

urlpatterns = [
    path('',include(router.urls)),
]