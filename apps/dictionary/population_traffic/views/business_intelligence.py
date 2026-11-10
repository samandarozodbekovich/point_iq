import json
from django.db.models import Avg, Sum
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.competitors.competitor.models import Competitor
from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel
from apps.dictionary.population_traffic.models.traffic_segment import TrafficSegmentModel
from apps.dictionary.population_traffic.models.traffic_note import TrafficNoteModel

from apps.citizens.population.models import Population
from apps.citizens.age_groups.models import AgeGroupPopulation
from apps.citizens.relationship_status.models import RelationshipStatusPopulation
from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation
from apps.areas.districts.models import District

from apps.competitors.competitor.tasks import fetch_and_update_competitors_2gis
from apps.shared.throttles import TwoGisApiThrottle, allow_paid_call


class BusinessIntelligenceView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
        except (TypeError, ValueError):
            return Response({"error": "lat va lng parametrlari talab qilinadi"}, status=400)

        query = request.query_params.get('query')
        category_name = request.query_params.get('category')
        radius = float(request.query_params.get('radius', 1500))
        user_point = Point(lng, lat, srid=4326)

        # 2. Ma'lumotlarni yig'ish (Background Task)
        if query and allow_paid_call(TwoGisApiThrottle, request, self):
            fetch_and_update_competitors_2gis.delay(query=query, category_name=category_name)

        # 3. Tahlil: Raqobatchilar, POI va Transport
        comp_qs = Competitor.objects.filter(location__distance_lte=(user_point, D(m=radius)))
        comp_count = comp_qs.count()
        avg_rating = comp_qs.aggregate(Avg('average_rating'))['average_rating__avg'] or 0

        poi_count = PointOfInterestModel.objects.filter(location__distance_lte=(user_point, D(m=radius))).count()
        transit_count = TrafficNoteModel.objects.filter(
            location__distance_lte=(user_point, D(m=radius)), node_type="transit"
        ).count()

        search_buffer = user_point.buffer(radius / 111000)
        high_traffic_roads = TrafficSegmentModel.objects.filter(
            line__intersects=search_buffer, intensity_level='high'
        ).count()

        # 4. Demografiya: Nuqta orqali Tumanni topish va ma'lumotlarni yig'ish
        demographics_data = {}
        pop_density = 0
        avg_income = 0

        # is_point_inside metodidan foydalanib tumanni topamiz
        target_district = None
        for district in District.objects.all():
            if district.is_point_inside(lat, lng):
                target_district = district
                break

        if target_district:
            # Aholi va Daromad
            pop = Population.objects.filter(district=target_district).first()
            if pop:
                pop_density = pop.population_density
                avg_income = pop.average_income

                # Yosh guruhlari
                age_stats = AgeGroupPopulation.objects.filter(population=pop).values(
                    'age_group__age_group'
                ).annotate(total=Sum('count'))

                # Oilaviy holat
                rel_stats = RelationshipStatusPopulation.objects.filter(population=pop).values(
                    'relationship_status__name_uz'
                ).annotate(total=Sum('count'))

                # Ta'lim va Iste'mol
                edu = PeopleEducation.objects.filter(district=target_district).first()
                consume = PeopleConsume.objects.filter(district=target_district).order_by('-year', '-month').first()

                demographics_data = {
                    "district_name": target_district.name_uz,
                    "general": {
                        "population_density": pop_density,
                        "average_income": avg_income,
                        "unemployment_rate": pop.unemployment_rate,
                        "male_count": pop.count_male,
                        "female_count": pop.count_female
                    },
                    "age_groups": {item['age_group__age_group']: item['total'] for item in age_stats},
                    "relationship_status": {item['relationship_status__name_uz']: item['total'] for item in rel_stats},
                    "infrastructure": {
                        "schools": edu.regional_school if edu else 0,
                        "kindergartens": edu.regional_kindergarten if edu else 0,
                        "bus_stations": consume.bus_station if consume else 0
                    }
                }

        # 5. INTEGRAL SCORE (Murakkab ball hisoblash)
        # Oqim va infrastruktura (POI + Traffic + Transit)
        flow_score = (poi_count * 1.5) + (high_traffic_roads * 8) + (transit_count * 5)
        # Demografiya vazni (Zichlik va Daromad)
        demographic_score = (pop_density / 500) + (avg_income / 10000)
        # Raqobat jarimasi
        competition_penalty = (comp_count * 4) + (10 if avg_rating > 4 else 0)

        final_score = max(0, min(100, int(flow_score + demographic_score - competition_penalty)))

        # 6. GeoJSON Map Data
        features = [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [c.longitude, c.latitude]},
            "properties": {
                "name": c.name_uz or c.name_ru,
                "type": "competitor",
                "rating": c.average_rating,
                "color": "blue"
            }
        } for c in comp_qs[:50]]

        return Response({
            "status": "success",
            "analysis": {
                "score": final_score,
                "recommendation": self._get_recommendation(final_score),
                "market_saturation": "Yuqori" if comp_count > 15 else "Past/O'rtacha"
            },
            "demographics": demographics_data,
            "dashboard": {
                "total_competitors": comp_count,
                "avg_competitor_rating": round(avg_rating, 1),
                "poi_magnets": poi_count,
                "transit_nodes": transit_count,
                "high_traffic_segments": high_traffic_roads,
            },
            "map_data": {
                "type": "FeatureCollection",
                "features": features
            }
        })

    def _get_recommendation(self, score):
        if score > 80: return "Ideal hudud. Aholi zichligi va oqim juda yuqori."
        if score > 55: return "Yaxshi tanlov. Barqaror mijoz bazasi shakllanishi mumkin."
        if score > 35: return "Xatarli hudud. Raqobatni qayta tahlil qiling."
        return "Tavsiya etilmaydi. Biznes uchun resurslar yetarli emas."