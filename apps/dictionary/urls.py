from django.urls import path
from apps.dictionary.cars.car_traffic.views import MapConfigView, MapPageView, GeocodeView


urlpatterns = [
    path('api/map-config/', MapConfigView.as_view(), name='map-config'),
    path('api/geocode/', GeocodeView.as_view(), name='geocode'),
    path('', MapPageView.as_view(), name='map-page'),
]