from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.measure import D
from django.core.cache import cache

from ..models.point_of_interest import PointOfInterestModel
from ..serializers.traffic import TrafficRequestSerializer
from ..services.traffic_analysis import TrafficAnalysis
from ...tasks.fetch_tashkent_data import PENDING_TTL, fetch_tashkent_data
from ...utils.fetch_tashkent_data import area_cache_key



class TrafficAnalysisPointView(APIView):
    def post(self, request):
        serializer = TrafficRequestSerializer(data=request.data)
        if serializer.is_valid():
            point = serializer.validated_data['point']
            radius = serializer.validated_data['radius']

            data_exists = PointOfInterestModel.objects.filter(
                location__distance_lte=(point, D(m=radius))
            ).exists()

            # An area that was already fetched and simply has no POIs is
            # analysed as it is; otherwise it would answer 202 forever.
            already_fetched = cache.get(area_cache_key("done", point.y, point.x, radius))

            if not data_exists and not already_fetched:
                # cache.add is atomic: only the first request queues a task,
                # later ones wait for it instead of hitting Overpass again.
                if cache.add(area_cache_key("pending", point.y, point.x, radius), True, timeout=PENDING_TTL):
                    fetch_tashkent_data.delay(point.y, point.x, radius)

                return Response({
                    "message": "Ushbu hudud bo'yicha ma'lumotlar yuklanmoqda. Iltimos, bir ozdan so'ng qayta urinib ko'ring.",
                    "status": "processing"
                }, status=status.HTTP_202_ACCEPTED)

            result = TrafficAnalysis.get_location_score(point, radius)
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

