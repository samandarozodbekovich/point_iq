import importlib
import json
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.areas.districts.models import District
from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.government_bodies.models import GovernmentBody
from apps.property.property_listing.models import PropertyListing
from apps.shared.functions import get_nearby_objects

DATA = Path(settings.BASE_DIR) / "data" / "districts"
LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


def geometry_of(name):
    feature = next(f for f in json.loads((DATA / name).read_text(encoding="utf-8"))["features"]
                   if f["geometry"]["type"] in ("Polygon", "MultiPolygon"))
    return GEOSGeometry(json.dumps(feature["geometry"]), srid=4326)


class DistrictLookupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for name in ("tashkent.geojson", "mirza-ulugbek.geojson", "chilanzar.geojson"):
            call_command("upload_districts", str(DATA / name), stdout=StringIO())
        cls.mirzo = geometry_of("mirza-ulugbek.geojson")
        cls.chilonzor = geometry_of("chilanzar.geojson")

    def test_point_in_second_part_of_multipolygon(self):
        # boundary_json kept only the first part, so this point used to match nothing.
        second_part = self.mirzo[1]
        point = second_part.point_on_surface
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
        ring = [list(c) for c in self.chilonzor[0][0].coords] if self.chilonzor.geom_type == "MultiPolygon" \
            else [list(c) for c in self.chilonzor[0].coords]
        d = District.objects.create(name_uz="Eski", boundary_json=ring[:-1])  # unclosed ring, as stored
        migration.backfill(django_apps, None)
        d.refresh_from_db()
        self.assertTrue(d.boundary.contains(self.chilonzor.point_on_surface))


@override_settings(CACHES=LOCMEM)
class CompetitorByDistrictTests(TestCase):
    def test_filter_by_district_uses_boundary(self):
        call_command("upload_districts", str(DATA / "chilanzar.geojson"), stdout=StringIO())
        district = District.objects.get()
        inside = district.boundary.point_on_surface
        cat = CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")
        Competitor.objects.create(category=cat, name_uz="Ichkarida", latitude=inside.y, longitude=inside.x)
        Competitor.objects.create(category=cat, name_uz="Tashqarida", latitude=40.0, longitude=60.0)

        r = APIClient().get("/api/competitors/competitor/", {"category": "Kafe", "district_id": district.id})
        self.assertEqual(r.status_code, 200)
        self.assertEqual([c["name_uz"] for c in r.data["results"]], ["Ichkarida"])


class NearbyObjectsTests(TestCase):
    def body(self, name, lat, lng):
        return GovernmentBody.objects.create(name_uz=name, address="-", schedule="-", phone_number="-",
                                             director="-", latitude=lat, longitude=lng)

    def test_radius_and_order(self):
        self.body("2km", 41.3180, 69.2797)
        self.body("0.5km", 41.3045, 69.2797)
        self.body("20km", 41.4800, 69.2797)
        self.body("no coords", None, None)
        result = get_nearby_objects(41.3000, 69.2797, radius_km=5, model=GovernmentBody)
        self.assertEqual([b.name_uz for b in result], ["0.5km", "2km"])

    def test_decimal_coordinates(self):
        PropertyListing.objects.create(property_type="flat", title="Yaqin", description="-", address="-",
                                       price=1, currency="USD", area_sq_m=1, rooms=1, floor=1,
                                       latitude=Decimal("41.300500"), longitude=Decimal("69.279700"))
        result = get_nearby_objects("41.3", "69.2797", model=PropertyListing)
        self.assertEqual([p.title for p in result], ["Yaqin"])
