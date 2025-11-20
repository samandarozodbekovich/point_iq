
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from hitcount.models import HitCount
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Competitor
from .serializers import CompetitorSerializer
from .tasks import fetch_and_update_competitors
from ...shared.functions import get_nearby_objects, hit_count
from ...shared.views.base_view_set import BaseModelViewSet



class CompetitorViewSet(BaseModelViewSet):
    model = Competitor
    serializer_class = CompetitorSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        content_type = ContentType.objects.get_for_model(instance)
        hit_count_obj, created = HitCount.objects.get_or_create(
            content_type=content_type,
            object_pk=instance.pk
        )

        hit_count(request, hit_count_obj)

        # response by serializer
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
        comp = self.get_object()

        if not comp.latitude or not comp.longitude:
            return Response({"error": "No coordinates available"}, status=400)

        nearby_objs = get_nearby_objects(comp.latitude, comp.longitude, model=Competitor)

        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"latitude": comp.latitude, "longitude": comp.longitude},
            "radius_km": 5,
            "count": len(nearby_objs),
            "results": serializer.data
        })

    @action(detail=True, methods=['get'])
    def nearby_location(self, request):
        try:
            lat = float(request.query_params.get("lat"))
            long = float(request.query_params.get("long"))
        except:
            return Response({"error": "long and lat are required"}, status=400)

        nearby_objs = get_nearby_objects(lat, long, model=Competitor)
        serializer = self.get_serializer(nearby_objs, many=True)
        return Response({
            "center": {"latitude":lat, "longitude":long},
            "radius_km": 5,
            "count": len(nearby_objs),
            "results": serializer.data
        })






