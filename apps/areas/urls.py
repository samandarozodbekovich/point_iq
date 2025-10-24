from rest_framework import routers
from apps.areas.areas.views import AreaViewset
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'areas', AreaViewset, basename='areas')
urlpatterns = [
    path('', include(router.urls)),
]