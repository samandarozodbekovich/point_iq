from django.db.models import Sum, Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.areas.places.models import Place
from apps.citizens.age_groups.models import AgeGroup
from apps.citizens.religions.models import Religion
from apps.competitors.competitor.models import Competitor
from apps.shared.views.base_view_set import BaseModelViewSet
from apps.areas.areas.models import Area
from apps.areas.areas.serializers import AreaSerializer


class AreaViewSet(BaseModelViewSet):
    model = Area
    serializer_class = AreaSerializer

    @action(detail=True, methods=["get"], url_path="details")
    def get_area_details(self, request, pk=None):
        try:
            area = Area.objects.select_related('district', 'city').get(pk=pk)
        except Area.DoesNotExist:
            return Response({"error": "Area not found"}, status=404)

        # Shu area ga tegishli barcha place lar
        places = Place.objects.filter(street__area=area)

        # Competitorlar soni

        competitor_data = (
            Competitor.objects
            .filter(place__in=places)
            .values("category__name_uz")
            .annotate(total=Count("id"))
        )

        competitors_result = [
            {"category": r["category__name_uz"], "count": r["total"]}
            for r in competitor_data
        ]


        # Diniy aholining umumiy soni
        religion_data = (

            Religion.objects
            .filter(population__apartment__in=places)
            .values("name_uz")
            .annotate(total=Sum("count"))
        )
        religion_result = [
            {"religion": r["religion__name_uz"], "count": r["total"]}
            for r in religion_data
        ]

        # Yosh guruhlar
        age_groups = (
            AgeGroup.objects
            .filter(population__apartment__in=places)
            .values("age_group")
            .annotate(total=Sum("count"))
        )
        age_group_result = [
            {"age_group": a["age_group"], "count": a["total"]}
            for a in age_groups
        ]

        # Umumiy ma'lumot
        data = {
            "city": area.city.name_uz,
            "district": area.district.name_uz,
            "area": area.name_uz,
            "competitors_count": competitors_result,
            "religion_population": religion_result,
            "age_groups": age_group_result,
        }

        return Response(data)



