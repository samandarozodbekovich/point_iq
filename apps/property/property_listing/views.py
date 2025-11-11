from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.competitors.utils import haversine
from apps.property.property_listing.models import PropertyListing
from apps.property.property_listing.serializers import PropertyListingSerializer
from apps.shared.views.base_deleted_items_view_set import BaseDeletedItemsViewSet


class PropertyListingViewSet(BaseDeletedItemsViewSet):
    model = PropertyListing
    serializer_class = PropertyListingSerializer

    def list(self, request):
        address = request.query_params.get("address")
        # Bazadagi mavjud ma’lumotlarni qaytarish
        properties = PropertyListing.objects.filter(
            address__icontains=address
        )
        serializer = self.get_serializer(properties, many=True)
        return Response({
            "status": "fetch_started",
            "address": address,
            "count": properties.count(),
            "results": serializer.data
        })

    # 🟡 2. ID bo‘yicha 5 km radiusdagi joylarni topish
    @action(detail=True, methods=['get'])
    def nearby(self, request, pk=None):
        try:
            comp = self.get_object()
        except PropertyListing.DoesNotExist:
            return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

        lat, lon = comp.latitude, comp.longitude
        if not lat or not lon:
            return Response({"error": "No coordinates available"}, status=status.HTTP_400_BAD_REQUEST)

        radius_km = 5
        nearby_objs = []
        for other in PropertyListing.objects.exclude(id=comp.id):
            if not other.latitude or not other.longitude:
                continue
            distance = haversine(lat, lon, other.latitude, other.longitude)
            if distance <= radius_km:
                nearby_objs.append(other)

        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "count": len(nearby_objs),
            "results": serializer.data
        })

    # 🔵 3. Foydalanuvchi koordinatasi (lat/lon) bo‘yicha 5 km radiusdagi joylar
    @action(detail=False, methods=['get'])
    def nearby_location(self, request):
        lat = request.query_params.get("lat")
        lon = request.query_params.get("lon")

        if not lat or not lon:
            return Response({"error": "lat and lon required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return Response({"error": "invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)

        radius_km = 5
        nearby_objs = []
        for property in PropertyListing.objects.all():
            if not property.latitude or not property.longitude:
                continue
            distance = haversine(lat, lon, property.latitude, property.longitude)
            if distance <= radius_km:
                nearby_objs.append(property)

        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "count": len(nearby_objs),
            "results": serializer.data
        })
