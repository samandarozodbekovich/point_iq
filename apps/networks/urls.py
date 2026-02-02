# app/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import CellTowerViewSet

router = routers.DefaultRouter()
router.register('cell-towers', CellTowerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
