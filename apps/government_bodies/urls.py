from django.urls import path, include
from rest_framework import routers

from apps.government_bodies.views.government_body import GovernmentBodyViewSet
from apps.government_bodies.views.government_worker import GovernmentWorkerViewSet

router = routers.DefaultRouter()
router.register(r'', GovernmentBodyViewSet, basename='government-body')
router.register(r'workers', GovernmentWorkerViewSet, basename='government-workers')

urlpatterns = [
    path('', include(router.urls)),
]