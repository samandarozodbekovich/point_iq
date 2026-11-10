from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch, Q
from hitcount.models import HitCount
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Competitor
from ..competitor_review.models import CompetitorReview
from apps.areas.districts.models import District
from .serializers import CompetitorSerializer, CompetitorAnalysisSerializer, LocationScoreSerializer
from ..competitor_categories.models import CompetitorCategory
from ..utils.calculate_location_score import calculate_location_score, get_poi_counts_in_radius

from ...shared.functions import hit_count
from ...shared.throttles import GoogleApiThrottle, TwoGisApiThrottle, allow_paid_call
from ...shared.views.base_view_set import BaseModelViewSet
from .tasks import fetch_google_competitors_task, fetch_and_update_competitors_2gis
from .services import fetch_and_save_nearby_competitors


class CompetitorViewSet(BaseModelViewSet):
    model = Competitor
    serializer_class = CompetitorSerializer
    lookup_field = 'pk'

    # Actions that call paid external APIs, mapped to their provider's budget.
    PAID_ACTION_THROTTLES = {
        'sync_2gis': TwoGisApiThrottle,
        'sync_google': GoogleApiThrottle,
    }

    def get_queryset(self):
        # Everything CompetitorSerializer reads, loaded in a fixed number of
        # queries instead of several per competitor.
        return Competitor.objects.select_related('category').prefetch_related(
            Prefetch('reviews', queryset=CompetitorReview.objects.select_related('user')),
            'hit_count_generic',
        )

    def get_permissions(self):
        # BaseModelViewSet.get_permissions ignores permission_classes, so an
        # @action(permission_classes=...) argument would have no effect here.
        if self.action in self.PAID_ACTION_THROTTLES:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_throttles(self):
        throttle_class = self.PAID_ACTION_THROTTLES.get(self.action)
        if throttle_class:
            return [throttle_class()]
        return super().get_throttles()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)
        hit_count_obj, _ = HitCount.objects.get_or_create(
            content_type=content_type,
            object_pk=instance.pk
        )
        hit_count(request, hit_count_obj)
        # The prefetched count predates this view; let the serializer reload it.
        getattr(instance, '_prefetched_objects_cache', {}).pop('hit_count_generic', None)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Kategoriya nomi (uz yoki ru)"),
        openapi.Parameter('district_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Tuman ID raqami"),
        openapi.Parameter('query', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Nomi yoki manzili bo'yicha qidiruv"),
    ])
    def list(self, request):
        category_name = request.query_params.get("category")
        district_id = request.query_params.get("district_id")
        query = request.query_params.get("query")

        if not category_name:
            return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)

        if district_id:
            return self.filter_by_district(district_id, category_name)

        queryset = self.get_queryset().filter(
            Q(category__name_uz__icontains=category_name) |
            Q(category__name_ru__icontains=category_name)
        )

        if query:
            queryset = queryset.filter(
                Q(address__icontains=query) |
                Q(name_uz__icontains=query) |
                Q(name_ru__icontains=query)
            )

        if not queryset.exists() and query and allow_paid_call(TwoGisApiThrottle, request, self):
            cat_obj = CompetitorCategory.objects.filter(
                Q(name_uz__icontains=category_name) | Q(name_ru__icontains=category_name)
            ).first()

            target_category_ru = cat_obj.name_ru if cat_obj else category_name

            fetch_and_update_competitors_2gis.delay(query, target_category_ru)

            return Response({
                "status": "loading",
                "message": "Ma'lumotlar bazada topilmadi. 2GIS'dan yuklanmoqda...",
                "count": 0,
                "results": []
            }, status=status.HTTP_202_ACCEPTED)

        return Response({
            "status": "success",
            "count": queryset.count(),
            "results": self.get_serializer(queryset, many=True).data
        })

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['query'],
            properties={
                'query': openapi.Schema(type=openapi.TYPE_STRING, description="Qidiruv so'zi (Manzil, shahar yoki brend)"),
                'category_name': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrlash uchun kategoriya (RU tilda)"),
            }
        ),
        operation_description="2GIS orqali matnli qidiruv va fonda bazaga yuklash"
    )
    @action(detail=False, methods=['post'], url_path='sync-2gis')
    def sync_2gis(self, request):
        query = request.data.get("query")
        category_name = request.data.get("category_name")

        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        task = fetch_and_update_competitors_2gis.delay(query, category_name)
        return Response({
            "status": "2GIS sync started",
            "task_id": task.id,
            "message": f"'{query}' bo'yicha ma'lumotlar fonda yuklanmoqda."
        }, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['lat', 'lng', 'category_id'],
            properties={
                'lat': openapi.Schema(type=openapi.TYPE_NUMBER),
                'lng': openapi.Schema(type=openapi.TYPE_NUMBER),
                'radius': openapi.Schema(type=openapi.TYPE_INTEGER, default=500),
                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Bazadagi kategoriya ID-si"),
            }
        ),
        operation_description="Google orqali radius bo'yicha fonda bazaga yuklash"
    )
    @action(detail=False, methods=['post'], url_path='sync-google')
    def sync_google(self, request):
        """Google orqali radius bo'yicha qidiruv (Celery task)"""
        lat = request.data.get("lat")
        lng = request.data.get("lng")
        radius = request.data.get("radius", 500)
        category_id = request.data.get("category_id")

        if not lat or not lng or not category_id:
            return Response({"error": "lat, lng and category_id are required"}, status=400)

        # Google API types mapping (View ichidagi map_to_google_type'ga o'xshash mantiq Task ichida bo'lishi kerak)
        task = fetch_google_competitors_task.delay(lat, lng, radius, category_id)
        return Response({
            "status": "Google sync started",
            "task_id": task.id,
            "message": "Belgilangan hudud bo'yicha Google ma'lumotlari fonda yuklanmoqda."
        }, status=status.HTTP_202_ACCEPTED)

    def filter_by_district(self, district_id, category):
        """Tuman chegarasi bo'yicha bazadan filterlash"""
        try:
            district = District.objects.get(id=district_id)
        except District.DoesNotExist:
            return Response({"error": "Tuman topilmadi"}, status=404)

        if district.boundary is None:
            results = self.get_queryset().none()
        else:
            # Point-in-polygon in the database, using the spatial index on
            # Competitor.location, instead of loading every match into Python.
            results = self.get_queryset().filter(
                Q(category__name_uz__icontains=category) | Q(category__name_ru__icontains=category),
                location__within=district.boundary,
            )

        return Response({
            "status": "success",
            "district": district.name_uz,
            "results": self.get_serializer(results, many=True).data
        })


class CompetitorAnalysisAPI(APIView):
    # Calls Google Places synchronously on every request.
    permission_classes = [IsAuthenticated]
    throttle_classes = [GoogleApiThrottle]

    @swagger_auto_schema(query_serializer=CompetitorAnalysisSerializer)
    def get(self, request):
        serializer = CompetitorAnalysisSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        lat = serializer.validated_data['lat']
        lng = serializer.validated_data['long']
        radius = serializer.validated_data['radius']
        category_id = serializer.validated_data.get('category_id')

        try:
            category_obj = CompetitorCategory.objects.get(id=category_id)
            google_type_id = category_obj.id
        except CompetitorCategory.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        analysis = fetch_and_save_nearby_competitors(lat, lng, radius, google_type_id)

        if "error" in analysis:
            return Response(analysis, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "summary": {
                "category": category_obj.name_uz,
                "total_found": analysis.get("total_found"),
                "new_added": analysis.get("created_count")
            },
            "results": analysis.get("data", {}).get("places", [])
        })



class PointIQScoreView(APIView):

    def get(self, request):
        serializer = LocationScoreSerializer(data=request.query_params)

        if serializer.is_valid():
            lat = serializer.validated_data['lat']
            lon = serializer.validated_data['lon']
            rent = serializer.validated_data.get('potential_rent')

            # 1. Skoringni hisoblaymiz
            score = calculate_location_score(lat, lon, potential_rent=rent)

            # 2. Qo'shimcha tahliliy ma'lumotlarni yig'amiz (Frontend uchun)
            poi_summary = get_poi_counts_in_radius(lat, lon)

            # 3. Biznes tavsiyasi
            recommendation = "Highly Recommended" if score > 75 else "Needs Review" if score > 50 else "Not Recommended"

            return Response({
                "status": "success",
                "coordinate": {"lat": lat, "lon": lon},
                "final_score": score,
                "recommendation": recommendation,
                "analysis_details": {
                    "competitor_count": poi_summary.get('fast_food', 0),
                    "nearby_universities": poi_summary.get('university', 0),
                    "metro_access": poi_summary.get('metro_station', 0) > 0,
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)