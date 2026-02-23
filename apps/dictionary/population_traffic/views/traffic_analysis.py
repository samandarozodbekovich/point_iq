from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.measure import D

from ..models.point_of_interest import PointOfInterestModel
from ..serializers.traffic import TrafficRequestSerializer
from ..services.traffic_analysis import TrafficAnalysis
from ...tasks.fetch_tashkent_data import fetch_tashkent_data



class TrafficAnalysisPointView(APIView):
    def post(self, request):
        serializer = TrafficRequestSerializer(data=request.data)
        if serializer.is_valid():
            point = serializer.validated_data['point']
            radius = serializer.validated_data['radius']

            data_exists = PointOfInterestModel.objects.filter(
                location__distance_lte=(point, D(m=radius))
            ).exists()

            if not data_exists:
                fetch_tashkent_data.delay(point.y, point.x, radius)

                return Response({
                    "message": "Ushbu hudud bo'yicha ma'lumotlar yuklanmoqda. Iltimos, bir ozdan so'ng qayta urinib ko'ring.",
                    "status": "processing"
                }, status=status.HTTP_202_ACCEPTED)

            result = TrafficAnalysis.get_location_score(point, radius)
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

