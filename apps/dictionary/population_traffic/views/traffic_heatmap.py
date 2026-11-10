
from django.contrib.gis.geos import Polygon
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.competitors.competitor.models import Competitor
from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel
from apps.dictionary.population_traffic.models.traffic_node import TrafficNodeModel
from apps.dictionary.population_traffic.models.traffic_segment import TrafficSegmentModel


# Roughly the whole of Tashkent; a map view never needs more at once.
MAX_BBOX_DEGREES = 0.5
# Per layer, so one dense layer can't crowd out the others.
MAX_FEATURES_PER_LAYER = 2000


class TrafficHeatmapView(APIView):
    def get(self, request):
        # 1. Filtrlarni olish
        layers = request.query_params.get('layers', 'all').split(',')

        features = []
        truncated = False

        # The bbox is required and validated. It used to be optional, and an
        # invalid one was silently ignored: either way the response was the
        # whole database as GeoJSON.
        bbox_polygon, error = self.parse_bbox(request.query_params.get('in_bbox'))
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        def limited(qs):
            nonlocal truncated
            rows = list(qs[:MAX_FEATURES_PER_LAYER + 1])
            if len(rows) > MAX_FEATURES_PER_LAYER:
                truncated = True
            return rows[:MAX_FEATURES_PER_LAYER]

        # 2. Qatlamlar bo'yicha ma'lumot yig'ish

        # NODES (Transport bog'lamalari)
        if 'all' in layers or 'node' in layers:
            qs = TrafficNodeModel.objects.all()
            qs = qs.filter(location__contained=bbox_polygon)
            for n in limited(qs):
                features.append(self._to_geojson(n.location, {
                    "weight": n.base_weight,
                    "color": "red",
                    "type": "node"
                }))

        # POI (Nuqtalar)
        if 'all' in layers or 'poi' in layers:
            qs = PointOfInterestModel.objects.all()
            qs = qs.filter(location__contained=bbox_polygon)

            for p in limited(qs):
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
            qs = qs.filter(location__contained=bbox_polygon)
            for c in limited(qs):
                features.append(self._to_geojson(c.location, {
                    "weight": (c.average_rating or 3) * 2,
                    "color": "blue",
                    "type": "competitor",
                    "label": c.name_uz
                }))

        # SEGMENTS (Yo'llar)
        if 'all' in layers or 'segment' in layers:
            qs = TrafficSegmentModel.objects.all()
            qs = qs.filter(line__intersects=bbox_polygon)
            for s in limited(qs):
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
            "features": features,
            "truncated": truncated,
        })

    @staticmethod
    def parse_bbox(value):
        """in_bbox=xmin,ymin,xmax,ymax (lon/lat). Returns (polygon, error)."""
        if not value:
            return None, "in_bbox=xmin,ymin,xmax,ymax is required"
        try:
            xmin, ymin, xmax, ymax = map(float, value.split(','))
        except ValueError:
            return None, "in_bbox must be four numbers: xmin,ymin,xmax,ymax"
        if not (-180 <= xmin < xmax <= 180 and -90 <= ymin < ymax <= 90):
            return None, "in_bbox must have xmin < xmax and ymin < ymax within lon/lat range"
        if xmax - xmin > MAX_BBOX_DEGREES or ymax - ymin > MAX_BBOX_DEGREES:
            return None, f"in_bbox may span at most {MAX_BBOX_DEGREES} degrees each way"
        return Polygon.from_bbox((xmin, ymin, xmax, ymax)), None

    def _to_geojson(self, location, properties):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [location.x, location.y]
            },
            "properties": properties
        }