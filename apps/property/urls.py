from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.property.property_listing.views import PropertyListingViewSet
from apps.property.property_images.views import PropertyImageViewSet

router = DefaultRouter()

router.register(r'', PropertyListingViewSet, basename='property-listing')
router.register(r'images', PropertyImageViewSet, basename='property-images')

urlpatterns = [
    path('', include(router.urls)),
]