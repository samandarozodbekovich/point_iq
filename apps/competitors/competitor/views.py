from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from hitcount.models import HitCount
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Competitor
from apps.areas.districts.models import District
from .serializers import CompetitorSerializer
from ...core.views import BaseBulkMethods
from ...shared.functions import get_nearby_objects, hit_count
from ...shared.views.base_view_set import BaseModelViewSet
from .tasks import fetch_and_update_competitors_2gis


class CompetitorViewSet(BaseModelViewSet, BaseBulkMethods):
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
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request):

        query = request.query_params.get("query")
        category = request.query_params.get("category")
        district_id = request.query_params.get("district_id")

        if not category:
            return Response(
                {"error": "category required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # District bo'yicha filter
        if district_id:
            return self.filter_by_district(district_id, category)

        # Oddiy qidiruv
        if not query:
            return Response(
                {"error": "query or district_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Database'dan qidiruv
        competitors = Competitor.objects.filter(
            Q(category__name_uz__icontains=category),
            Q(Q(address__icontains=query) | Q(name_uz__icontains=query))
        )

        results = self._prepare_results(competitors)

        # MUHIM: Agar database'da ma'lumot bo'lmasa, background'da API dan yukla
        if not competitors.exists():
            # Category ni Russian nomiga o'zgartiramiz (2GIS uchun)
            try:
                category_obj = Competitor.objects.filter(
                    category__name_uz__icontains=category
                ).first()
                category_name_ru = category_obj.category.name_ru if category_obj else category
            except:
                category_name_ru = category

            # Background task
            fetch_and_update_competitors_2gis.delay(query, category_name_ru)

            return Response({
                "query": query,
                "category": category,
                "count": 0,
                "results": [],
                "status": "loading",
                "message": "No data in database. Fetching from 2GIS... Please refresh in a few seconds"
            }, status=status.HTTP_202_ACCEPTED)

        return Response({
            "query": query,
            "category": category,
            "count": competitors.count(),
            "results": results,
            "status": "success"
        })

    @action(detail=False, methods=['post'], url_path='search-2gis')
    def search_2gis(self, request):

        query = request.data.get("query")
        category_name = request.data.get("category_name")

        if not query or not category_name:
            return Response(
                {"error": "query and category_name required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Background task
        task = fetch_and_update_competitors_2gis.delay(query, category_name)

        return Response({
            "status": "Task started",
            "task_id": task.id,
            "query": query,
            "category_name": category_name,
            "message": "Data is being fetched. Check back soon."
        }, status=status.HTTP_202_ACCEPTED)

    def filter_by_district(self, district_id, category):
        try:
            district = District.objects.get(id=district_id)
        except District.DoesNotExist:
            return Response(
                {"error": f"Tuman topilmadi: ID={district_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not district.boundary_json:
            return Response(
                {"error": f"Bu tumanning boundary ma'lumotlari yo'q: {district.name_uz}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        all_competitors = Competitor.objects.filter(
            category__name_uz__icontains=category,
            latitude__isnull=False,
            longitude__isnull=False
        )

        competitors_in_district = [
            comp for comp in all_competitors
            if district.is_point_inside(comp.latitude, comp.longitude)
        ]

        results = self._prepare_results(competitors_in_district)

        return Response({
            "status": "success",
            "district": {
                "id": district.id,
                "name_uz": district.name_uz,
                "name_ru": district.name_ru,
                "city": district.city.name_uz if district.city else None
            },
            "category": category,
            "count": len(competitors_in_district),
            "results": results
        })

    @action(detail=False, methods=['get'], url_path='by-district')
    def by_district(self, request):
        district_id = request.query_params.get("district_id")
        category = request.query_params.get("category")

        if not district_id or not category:
            return Response(
                {"error": "district_id va category parametrlari kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return self.filter_by_district(district_id, category)

    @action(detail=False, methods=['get'], url_path='districts')
    def list_districts(self, request):
        city_id = request.query_params.get("city_id")

        districts = District.objects.select_related('city').all()
        if city_id:
            districts = districts.filter(city_id=city_id)

        data = [{
            "id": d.id,
            "name_uz": d.name_uz,
            "name_ru": d.name_ru,
            "name_cyr": d.name_cyr,
            "city": d.city.name_uz if d.city else None,
            "has_boundary": d.boundary_json is not None
        } for d in districts]

        return Response({"count": len(data), "results": data})

    @action(detail=False, methods=['post'], url_path='check-point')
    def check_point(self, request):
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if not latitude or not longitude:
            return Response(
                {"error": "latitude va longitude kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        districts = District.objects.exclude(boundary_json__isnull=True)

        found_districts = [
            {
                "id": d.id,
                "name_uz": d.name_uz,
                "name_ru": d.name_ru,
                "city": d.city.name_uz if d.city else None
            }
            for d in districts
            if d.is_point_inside(latitude, longitude)
        ]

        return Response({
            "latitude": float(latitude),
            "longitude": float(longitude),
            "found_districts": found_districts,
            "count": len(found_districts)
        })

    def _prepare_results(self, competitors):
        """Natijalarni tayyorlash"""
        results = []
        competitor_list = list(competitors) if not isinstance(competitors, list) else competitors

        for comp in competitor_list:
            serializer = self.get_serializer(comp)
            content_type = ContentType.objects.get_for_model(comp)
            hit_count_obj, _ = HitCount.objects.get_or_create(
                content_type=content_type,
                object_pk=comp.pk
            )

            comp_data = serializer.data
            comp_data.update({
                "total_hits": hit_count_obj.hits,
                "average_rating": comp.average_rating,
                "review_count": comp.review_count
            })
            results.append(comp_data)

        return results

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

    @action(detail=False, methods=['get'], url_path='nearby-location')
    def nearby_location(self, request):
        try:
            lat = float(request.query_params.get("lat"))
            long = float(request.query_params.get("long"))
        except:
            return Response({"error": "long and lat are required"}, status=400)

        nearby_objs = get_nearby_objects(lat, long, model=Competitor)
        serializer = self.get_serializer(nearby_objs, many=True)

        return Response({
            "center": {"latitude": lat, "longitude": long},
            "radius_km": 5,
            "count": len(nearby_objs),
            "results": serializer.data
        })