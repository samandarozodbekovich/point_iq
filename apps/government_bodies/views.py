from rest_framework.decorators import action
from rest_framework.response import Response

from apps.government_bodies.models import GovernmentBody
from apps.government_bodies.serializers import GovernmentBodySerializer
from apps.shared.functions import get_nearby_objects
from apps.shared.views.base_view_set import BaseModelViewSet


class GovernmentBodyViewSet(BaseModelViewSet):
    model = GovernmentBody
    serializer_class = GovernmentBodySerializer

    @action(methods=['get'], detail=True)
    def nearby(self, request, pk=None):
        branch = self.get_object()

        if branch.latitude is None or branch.longitude is None:
            return Response({"error": "No coordinates available"}, status=400)

        nearby_objs = get_nearby_objects(branch.latitude, branch.longitude, model=GovernmentBody)
        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center":{"lat":branch.latitude,"lng":branch.longitude},
            "radius":5,
            "count":len(nearby_objs),
            "objects":serializer.data
        })

    @action(methods=['get'], detail=True)
    def nearby_location(self,request):
        try:
            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
        except:
            return Response({"error": "No coordinates available"}, status=400)

        nearby_objs = get_nearby_objects(lat, lng, model=GovernmentBody)
        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center":{"lat":lat,"lng":lng},
            "radius":5,
            "count":len(nearby_objs),
            "objects":serializer.data
        })