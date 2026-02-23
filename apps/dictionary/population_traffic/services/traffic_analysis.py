
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from apps.competitors.competitor.models import Competitor
from ..models.point_of_interest import PointOfInterestModel
from ..models.traffic_note import TrafficNoteModel
from ..models.traffic_segment import TrafficSegmentModel


class TrafficAnalysis:
    @staticmethod
    def get_location_score(point, radius=500):
        # 1. Traffic Nodes & POIs (Attraction Force)
        nodes = TrafficNoteModel.objects.filter(
            location__distance_lte=(point, D(m=radius))
        ).annotate(distance=Distance("location", point))

        # POI larni ham qo'shdik
        pois = PointOfInterestModel.objects.filter(
            location__distance_lte=(point, D(m=radius))
        ).annotate(distance=Distance("location", point))

        total_score = 0
        for item in list(nodes) + list(pois):
            dist_m = item.distance.m
            decay_factor = 1 / (1 + (dist_m / 100))
            # Node uchun base_weight, POI uchun attraction_factor
            weight = getattr(item, 'base_weight', getattr(item, 'attraction_factor', 5))
            total_score += (weight * 10) * decay_factor

        # 2. Segments (Infrastructure Bonus)
        nearby_segments = TrafficSegmentModel.objects.filter(
            line__distance_lte=(point, D(m=50))
        )
        segment_bonus = sum([50 if s.intensity_level == 'high' else 20 for s in nearby_segments])
        total_score += segment_bonus

        # 3. Competitors (Cannibalization Risk)
        lat, lng = point.y, point.x
        nearby_competitors = Competitor.objects.filter(
            latitude__range=(lat - 0.005, lat + 0.005),  # ~500m
            longitude__range=(lng - 0.007, lng + 0.007)
        )

        # Market Status Logic
        comp_count = nearby_competitors.count()
        if comp_count > 10:
            market_status = "O'ta to'yingan (Qizil)"
        elif comp_count > 4:
            market_status = "Raqobat mavjud (Sariq)"
        else:
            market_status = "Ochiq (Yashil)"

        return {
            "total_score": round(total_score, 2),
            "market_analysis": {
                "status": market_status,
                "competitor_count": comp_count,
                "avg_rating": round(sum([c.average_rating or 0 for c in nearby_competitors]) / (comp_count or 1), 1)
            }
        }