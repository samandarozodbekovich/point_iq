from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.citizens.age_groups.views import AgeGroupViewSet
from apps.citizens.ethnicities.views import EthnicityViewSet
from apps.citizens.ethnicity_count.views import EthnicityCountViewSet
from apps.citizens.population.views import PopulationViewSet
from apps.citizens.population_statistic.views import PopulationStatisticViewSet
from apps.citizens.relationship_counts.views import RelationshipCountViewSet
from apps.citizens.relationship_status.views import RelationshipStatusViewSet
from apps.citizens.religion_counts.views import ReligionCountViewSet
from apps.citizens.religions.views import ReligionViewSet

router = DefaultRouter()
router.register(r'age-groups', AgeGroupViewSet, basename='age-groups')
router.register(r'ethnicities', EthnicityViewSet, basename='ethnicities')
router.register(r'ethnicity-counts', EthnicityCountViewSet, basename='ethnicity-counts')
router.register(r'populations', PopulationViewSet, basename='populations')
router.register(r'population-statistics', PopulationStatisticViewSet, basename='population-statistics')
router.register(r'relationship-counts', RelationshipCountViewSet, basename='relationship-counts')
router.register(r'relationship-status', RelationshipStatusViewSet, basename='relationship-status')
router.register(r'religion-counts', ReligionCountViewSet, basename='religion-counts')
router.register(r'religions', ReligionViewSet, basename='religions')


urlpatterns = [
    path('', include(router.urls)),
]