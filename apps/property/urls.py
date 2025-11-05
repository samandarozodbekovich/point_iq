from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.property.property_listing.views import PropertyListingViewSet
from apps.property.property_price_history.views import PropertyPriceHistoryViewSet
from apps.property.property_images.views import PropertyImageViewSet
from apps.property.property_feature.views import PropertyFeatureViewSet

router = DefaultRouter()

router.register(r'', PropertyListingViewSet, basename='property-listing')
router.register(r'images', PropertyImageViewSet, basename='property-images')
router.register(r'feature', PropertyFeatureViewSet, basename='property-feature')
router.register(r'price-history', PropertyPriceHistoryViewSet, basename='price-history')

urlpatterns = [
    path('', include(router.urls)),
]