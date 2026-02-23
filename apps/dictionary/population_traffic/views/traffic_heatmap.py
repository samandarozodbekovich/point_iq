
from django.contrib.gis.geos import Polygon
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.competitors.competitor.models import Competitor
from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel
from apps.dictionary.population_traffic.models.traffic_note import TrafficNoteModel
from apps.dictionary.population_traffic.models.traffic_segment import TrafficSegmentModel


class TrafficHeatmapView(APIView):
    def get(self, request):
        # 1. Filtrlarni olish
        bbox_param = request.query_params.get('in_bbox')
        layers = request.query_params.get('layers', 'all').split(',')

        features = []

        # BBOX polygonini tayyorlash
        bbox_polygon = None
        if bbox_param:
            try:
                xmin, ymin, xmax, ymax = map(float, bbox_param.split(','))
                bbox_polygon = Polygon.from_bbox((xmin, ymin, xmax, ymax))
            except ValueError:
                pass

        # 2. Qatlamlar bo'yicha ma'lumot yig'ish

        # NODES (Transport bog'lamalari)
        if 'all' in layers or 'node' in layers:
            qs = TrafficNoteModel.objects.all()
            if bbox_polygon: qs = qs.filter(location__contained=bbox_polygon)
            for n in qs:
                features.append(self._to_geojson(n.location, {
                    "weight": n.base_weight,
                    "color": "red",
                    "type": "node"
                }))

        # POI (Nuqtalar)
        if 'all' in layers or 'poi' in layers:
            qs = PointOfInterestModel.objects.all()
            if bbox_polygon:
                qs = qs.filter(location__contained=bbox_polygon)

            for p in qs:
                weight = getattr(p, 'attraction_factor', 1.0)
                color = getattr(p, 'zone_color', "orange") or "orange"
                category = getattr(p, 'category', "general")

                features.append(self._to_geojson(p.location, {
                    "weight": weight,
                    "color": color,
                    "type": "poi",
                    "category": category
                }))

        # COMPETITORS (Raqobatchilar)
        if 'all' in layers or 'competitor' in layers:
            qs = Competitor.objects.filter(location__isnull=False)
            if bbox_polygon: qs = qs.filter(location__contained=bbox_polygon)
            for c in qs:
                features.append(self._to_geojson(c.location, {
                    "weight": (c.average_rating or 3) * 2,
                    "color": "blue",
                    "type": "competitor",
                    "label": c.name_uz
                }))

        # SEGMENTS (Yo'llar)
        if 'all' in layers or 'segment' in layers:
            qs = TrafficSegmentModel.objects.all()
            if bbox_polygon: qs = qs.filter(line__intersects=bbox_polygon)
            for s in qs:
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": s.line.coords},
                    "properties": {
                        "color": s.zone_color,  # Biz fetch_data da saqlagan rang
                        "weight": 3 if s.intensity_level == "high" else 1.5,
                        "type": "segment",
                        "street_name": s.street_name
                    }
                })

        return Response({
            "type": "FeatureCollection",
            "features": features
        })

    def _to_geojson(self, location, properties):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [location.x, location.y]
            },
            "properties": properties
        }