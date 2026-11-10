from django.urls import path, include
from rest_framework import routers

from apps.government_bodies.views.government_body import GovernmentBodyViewSet
from apps.government_bodies.views.government_worker import GovernmentWorkerViewSet

router = routers.DefaultRouter()
# Order matters: the empty prefix generates ^(?P<pk>[^/.]+)/$, which would
# match workers/ as pk="workers" if it came first. Specific prefixes go first.
router.register(r'workers', GovernmentWorkerViewSet, basename='government-workers')
router.register(r'', GovernmentBodyViewSet, basename='government-body')

urlpatterns = [
    path('', include(router.urls)),
]