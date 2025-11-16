from django.urls import path, include
from rest_framework import routers


from apps.areas.cities.views import CityViewSet
from apps.areas.districts.views import DistrictViewSet

router = routers.DefaultRouter()

router.register(r'cities', CityViewSet, basename='cities')
router.register(r'districts', DistrictViewSet, basename='districts')


urlpatterns = [
    path('', include(router.urls)),
]


