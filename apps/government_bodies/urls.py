from django.urls import path, include
from rest_framework import routers

from apps.government_bodies.views import GovernmentBodyViewSet

router = routers.DefaultRouter()
router.register(r'', GovernmentBodyViewSet, basename='government-body')

urlpatterns = [
    path('', include(router.urls)),
]