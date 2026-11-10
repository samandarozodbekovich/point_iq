from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.property.property_listing.views import PropertyListingViewSet
from apps.property.property_images.views import PropertyImageViewSet

router = DefaultRouter()

# Order matters: the empty prefix generates ^(?P<pk>[^/.]+)/$, which would
# match images/ as pk="images" if it came first. Specific prefixes go first.
router.register(r'images', PropertyImageViewSet, basename='property-images')
router.register(r'', PropertyListingViewSet, basename='property-listing')

urlpatterns = [
    path('', include(router.urls)),
]