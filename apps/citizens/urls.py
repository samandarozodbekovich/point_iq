from django.urls import path

from apps.citizens.age_groups.views import AgeGroupAPIView, AgeGroupPopulationAPIView
from apps.citizens.ethnicities.views import EthnicityAPIView, EthnicityPopulationAPIView
from apps.citizens.population.views import PopulationAPIView
from apps.citizens.relationship_status.views import RelationshipStatusAPIView, RelationshipStatusPopulationAPIView
from apps.citizens.religions.views import ReligionAPIView, ReligionCountAPIView


urlpatterns = [
    path('age-group/', AgeGroupAPIView.as_view()),
    path('age-group/<int:pk>/', AgeGroupAPIView.as_view()),
    path('age-group-population/', AgeGroupPopulationAPIView.as_view()),
    path('age-group-population/<int:pk>/', AgeGroupPopulationAPIView.as_view()),
    path('ethnicity/', EthnicityAPIView.as_view()),
    path('ethnicity/<int:pk>/', EthnicityAPIView.as_view()),
    path('ethnicity-population/', EthnicityPopulationAPIView.as_view()),
    path('ethnicity-population/<int:pk>/', EthnicityPopulationAPIView.as_view()),
    path('population/', PopulationAPIView.as_view()),
    path('population/<int:pk>/', PopulationAPIView.as_view()),
    path('relationship-status/', RelationshipStatusAPIView.as_view()),
    path('relationship-status/<int:pk>/', RelationshipStatusAPIView.as_view()),
    path('relationship-status-population/', RelationshipStatusPopulationAPIView.as_view()),
    path('relationship-status-population/<int:pk>/', RelationshipStatusPopulationAPIView.as_view()),
    path('religion/', ReligionAPIView.as_view()),
    path('religion/<int:pk>/', ReligionAPIView.as_view()),
    path('religion-count/', ReligionCountAPIView.as_view()),
    path('religion-count/<int:pk>/', ReligionCountAPIView.as_view()),

]