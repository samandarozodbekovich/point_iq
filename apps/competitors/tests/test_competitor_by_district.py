"""GET /api/competitors/competitor/?district_id= (CompetitorViewSet.filter_by_district)."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.areas.districts.models import District
from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.shared.testing import DISTRICTS_DIR, LOCMEM_CACHE


@override_settings(CACHES=LOCMEM_CACHE)
class CompetitorByDistrictTests(TestCase):
    def test_filter_by_district_uses_boundary(self):
        call_command("upload_districts", str(DISTRICTS_DIR / "chilanzar.geojson"), stdout=StringIO())
        district = District.objects.get()
        inside = district.boundary.point_on_surface
        cat = CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")
        Competitor.objects.create(category=cat, name_uz="Ichkarida", latitude=inside.y, longitude=inside.x)
        Competitor.objects.create(category=cat, name_uz="Tashqarida", latitude=40.0, longitude=60.0)

        r = APIClient().get("/api/competitors/competitor/", {"category": "Kafe", "district_id": district.id})
        self.assertEqual(r.status_code, 200)
        self.assertEqual([c["name_uz"] for c in r.data["results"]], ["Ichkarida"])
