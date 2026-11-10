from rest_framework.decorators import action
from rest_framework.response import Response

from apps.property.property_listing.models import PropertyListing
from apps.property.property_listing.serializers import PropertyListingSerializer
from apps.shared.functions import get_nearby_objects, parse_lat_lng
from apps.shared.views.base_deleted_items_view_set import BaseDeletedItemsViewSet


class PropertyListingViewSet(BaseDeletedItemsViewSet):
    model = PropertyListing
    serializer_class = PropertyListingSerializer

    def list(self, request):
        address = request.query_params.get("address")
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

    @action(methods=['get'], detail=True)
    def nearby(self, request, pk=None):
        branch = self.get_object()

        if branch.latitude is None or branch.longitude is None:
            return Response({"error": "No coordinates available"}, status=400)

        nearby_objs = get_nearby_objects(branch.latitude, branch.longitude, model=PropertyListing)
        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"lat": branch.latitude, "lng": branch.longitude},
            "radius": 5,
            "count": len(nearby_objs),
            "objects": serializer.data
        })

    # detail=False: it works on ?lat=&lng=, not on an object. As a detail
    # action the router passed a pk the method doesn't accept (500).
    @action(methods=['get'], detail=False)
    def nearby_location(self, request):
        coords = parse_lat_lng(request.query_params)
        if coords is None:
            return Response({"error": "Valid lat and lng query parameters are required"}, status=400)
        lat, lng = coords

        nearby_objs = get_nearby_objects(lat, lng, model=PropertyListing)
        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"lat": lat, "lng": lng},
            "radius": 5,
            "count": len(nearby_objs),
            "objects": serializer.data
        })

