from django.urls import path,include
from rest_framework.routers import DefaultRouter

from apps.citizens.age_groups.views import AgeGroupViewSet, AgeGroupPopulationViewSet
from apps.citizens.population.views import PopulationViewSet
from apps.citizens.relationship_status.views import RelationshipStatusViewSet, RelationshipStatusPopulationViewSet
from apps.citizens.people_consume.views import PeopleConsumeViewSet
from apps.citizens.people_education.views import PeopleEducationViewSet

router = DefaultRouter()
router.register('age-groups', AgeGroupViewSet, basename='age-groups')
router.register('population', PopulationViewSet, basename='population')
router.register('relationship-status', RelationshipStatusViewSet, basename='relationship-status')
router.register('relationship-status-population', RelationshipStatusPopulationViewSet, basename='relationship-status-population')
router.register('age_group-population', AgeGroupPopulationViewSet, basename='age-group-population')
router.register('consume', PeopleConsumeViewSet, basename='people-consume')
router.register('education', PeopleEducationViewSet, basename='people-education')

urlpatterns = [
    path('',include(router.urls)),
]