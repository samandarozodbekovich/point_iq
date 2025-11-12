from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from hitcount.models import HitCount
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from math import radians, cos, sin, asin, sqrt

from .models import Competitor
from .serializers import CompetitorSerializer
from .tasks import fetch_and_update_competitors
from ...shared.views.base_view_set import BaseModelViewSet


def haversine(lat1, lon1, lat2, lon2):
    """2 nuqta orasidagi masofani km da hisoblaydi."""
    R = 6371
    if not all([lat1, lon1, lat2, lon2]):
        return 9999
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


class CompetitorViewSet(BaseModelViewSet):
    model = Competitor
    serializer_class = CompetitorSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # HitCount obyektini olish yoki yaratish
        content_type = ContentType.objects.get_for_model(instance)
        hit_count_obj, created = HitCount.objects.get_or_create(
            content_type=content_type,
            object_pk=instance.pk
        )

        # Hit qo‘shish (bitta foydalanuvchi bir necha marta kirsa ham faqat 1 ta hit)
        self.hit_count(request, hit_count_obj)

        # Seriazlizer orqali javob berish
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Asenkron API fetch (and give info from database)
    def list(self, request):
        query = request.query_params.get("query")  # city yoki street
        category = request.query_params.get("category")

        if not query or not category:
            return Response({"error": "query and category required"}, status=status.HTTP_400_BAD_REQUEST)

        # Celery works
        fetch_and_update_competitors.delay(query, category)

        # info from database
        competitors = Competitor.objects.filter(
            Q(category__name_uz__icontains=category),
            Q(Q(address__icontains=query) | Q(name_uz__icontains=query))
        )
        results = []
        for comp in competitors:
            serializer = self.get_serializer(comp)

            content_type = ContentType.objects.get_for_model(comp)
            hit_count_obj, _ = HitCount.objects.get_or_create(
                content_type=content_type,
                object_pk=comp.pk
            )
            total_hits = hit_count_obj.hits

            comp_data = serializer.data
            comp_data.update({
                "total_hits": total_hits,
                "average_rating": comp.average_rating,
                "review_count": comp.review_count
            })
            results.append(comp_data)

        return Response({
            "status": "fetch_started",
            "query": query,
            "category": category,
            "count": competitors.count(),
            "results": results
        })

    @action(detail=True, methods=['get'])
    def nearby(self, request, pk=None):
        try:
            comp = self.get_object()
        except Competitor.DoesNotExist:
            return Response({"error": "Competitor not found"}, status=status.HTTP_404_NOT_FOUND)

        lat, lon = comp.latitude, comp.longitude
        if not lat or not lon:
            return Response({"error": "No coordinates available"}, status=status.HTTP_400_BAD_REQUEST)

        radius_km = 5
        nearby_objs = []
        for other in Competitor.objects.exclude(id=comp.id):
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

    # Foydalanuvchi koordinatasi (lat/lon) bo‘yicha 5 km radiusdagi joylar
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
        for comp in Competitor.objects.all():
            if not comp.latitude or not comp.longitude:
                continue
            distance = haversine(lat, lon, comp.latitude, comp.longitude)
            if distance <= radius_km:
                nearby_objs.append(comp)

        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"latitude": lat, "longitude": lon},
            "radius_km": radius_km,
            "count": len(nearby_objs),
            "results": serializer.data
        })



