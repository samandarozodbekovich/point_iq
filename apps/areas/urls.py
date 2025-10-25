from django.urls import path, include
from rest_framework import routers

from apps.areas.areas.views import AreaViewSet
from apps.areas.cities.views import CityViewSet
from apps.areas.districts.views import DistrictViewSet
from apps.areas.places.views import PlaceViewSet
from apps.areas.streets.views import StreetViewSet


router = routers.DefaultRouter()

router.register(r'areas', AreaViewSet, basename='areas')
router.register(r'cities', CityViewSet, basename='cities')
router.register(r'districts', DistrictViewSet, basename='districts')
router.register(r'places', PlaceViewSet, basename='places')
router.register(r'streets', StreetViewSet, basename='streets')


urlpatterns = [
    path('', include(router.urls)),
]


