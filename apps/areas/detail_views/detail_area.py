# apps/areas/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from apps.areas.areas.models import Area
from apps.competitors.competitor.models import Competitor
from apps.citizens.religion_counts.models import ReligionCount
from apps.citizens.age_groups.models import AgeGroup
from apps.areas.places.models import Place

class AreaDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            area = Area.objects.get(pk=pk)
        except Area.DoesNotExist:
            return Response({"error": "Area not found"}, status=404)

        # Ushbu area ichidagi place lar
        places = Place.objects.filter(area=area)

        #  Competitorlar soni
        competitors_count = Competitor.objects.filter(place__in=places).count()

        # Diniy aholining umumiy soni (religion bo‘yicha)
        religion_data = (
            ReligionCount.objects
            .filter(population__place__in=places)
            .values("religion__name_uz")
            .annotate(total=Sum("count"))
        )
        religion_result = [
            {"religion": r["religion__name_uz"], "count": r["total"]}
            for r in religion_data
        ]

        # Age group ma’lumotlari (agar alohida jadvalda saqlanayotgan bo‘lsa)
        # Bu qismni o‘zingning modeli bilan moslashtirasan
        age_groups = (
            AgeGroup.objects.all().values("age_group")  # bu yerda agar count bor bo‘lsa sum qilinadi
        )

        data = {
            "area": area.name_uz,
            "district": area.district.name_uz,
            "competitors_count": competitors_count,
            "religion_population": religion_result,
            "age_groups": list(age_groups)
        }

        return Response(data)
