from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.test import APIClient

from apps.dictionary.population_traffic.models.point_of_interest import PointOfInterestModel
from apps.dictionary.population_traffic.views import traffic_heatmap


class HeatmapBboxTests(TestCase):
    url = "/api/statistics/heatmap/"

    def setUp(self):
        for i, (lng, lat) in enumerate([(69.20, 41.30), (69.21, 41.31), (69.90, 41.90)]):
            PointOfInterestModel.objects.create(name=f"p{i}", category="cafe", location=Point(lng, lat, srid=4326),
                                                influence_radius=500)

    def get(self, **params):
        return APIClient().get(self.url, {"layers": "poi", **params})

    def test_bbox_is_required_and_validated(self):
        self.assertEqual(self.get().status_code, 400)
        self.assertEqual(self.get(in_bbox="a,b,c,d").status_code, 400)
        self.assertEqual(self.get(in_bbox="69.3,41.2,69.1,41.4").status_code, 400)  # xmin > xmax
        self.assertEqual(self.get(in_bbox="68.0,40.0,70.0,42.0").status_code, 400)  # too large

    def test_only_features_inside_bbox(self):
        r = self.get(in_bbox="69.1,41.2,69.3,41.4")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["features"]), 2)
        self.assertFalse(r.data["truncated"])

    def test_per_layer_cap(self):
        original = traffic_heatmap.MAX_FEATURES_PER_LAYER
        traffic_heatmap.MAX_FEATURES_PER_LAYER = 1
        try:
            r = self.get(in_bbox="69.1,41.2,69.3,41.4")
        finally:
            traffic_heatmap.MAX_FEATURES_PER_LAYER = original
        self.assertEqual(len(r.data["features"]), 1)
        self.assertTrue(r.data["truncated"])
