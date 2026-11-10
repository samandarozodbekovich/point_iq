"""District.find_containing, upload_districts and migration 0002_district_boundary."""
import importlib
from io import StringIO

from django.apps import apps as django_apps
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from apps.areas.districts.models import District
from apps.shared.testing import DISTRICTS_DIR, district_geometry


class DistrictLookupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for name in ("tashkent.geojson", "mirza-ulugbek.geojson", "chilanzar.geojson"):
            call_command("upload_districts", str(DISTRICTS_DIR / name), stdout=StringIO())
        cls.mirzo = district_geometry("mirza-ulugbek.geojson")
        cls.chilonzor = district_geometry("chilanzar.geojson")

    def test_point_in_second_part_of_multipolygon(self):
        # boundary_json kept only the first part, so this point used to match nothing.
        point = self.mirzo[1].point_on_surface
        self.assertFalse(self.mirzo[0].contains(point))
        found = District.find_containing(point.y, point.x)
        self.assertIsNotNone(found)
        self.assertEqual(found.boundary.num_geom, 2)

    def test_district_wins_over_whole_city(self):
        point = self.chilonzor.point_on_surface
        found = District.find_containing(point.y, point.x)
        # The city boundary also contains the point; the smaller district must win.
        self.assertEqual(District.objects.filter(boundary__contains=point).count(), 2)
        self.assertTrue(self.chilonzor.equals(found.boundary))

    def test_outside_every_district(self):
        self.assertIsNone(District.find_containing(40.0, 60.0))

    def test_lookup_is_one_query(self):
        point = self.chilonzor.point_on_surface
        with CaptureQueriesContext(connection) as ctx:
            District.find_containing(point.y, point.x)
        self.assertEqual(len(ctx.captured_queries), 1)

    def test_backfill_migration(self):
        migration = importlib.import_module("apps.areas.migrations.0002_district_boundary")
        polygon = self.chilonzor[0] if self.chilonzor.geom_type == "MultiPolygon" else self.chilonzor
        ring = [list(c) for c in polygon[0].coords]
        d = District.objects.create(name_uz="Eski", boundary_json=ring[:-1])  # unclosed ring, as stored
        migration.backfill(django_apps, None)
        d.refresh_from_db()
        self.assertTrue(d.boundary.contains(self.chilonzor.point_on_surface))
