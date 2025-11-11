from django.urls import path, include
from rest_framework import routers


from apps.areas.cities.views import CityViewSet
from apps.areas.districts.views import DistrictViewSet
from apps.areas.address.views import AddressViewSet


router = routers.DefaultRouter()

router.register(r'cities', CityViewSet, basename='cities')
router.register(r'districts', DistrictViewSet, basename='districts')
router.register(r'addresses', AddressViewSet, basename='addresses')


urlpatterns = [
    path('', include(router.urls)),
]


