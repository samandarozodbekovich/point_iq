"""Competitor endpoints that spend Google/2GIS quota: login required, per-provider hourly limits.

Celery tasks and Google calls are mocked.
"""
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.shared.testing import LOCMEM_CACHE
from apps.users.models.user import User

VIEWS = "apps.competitors.competitor.views"


@override_settings(CACHES=LOCMEM_CACHE)
class PaidApiAccessTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="998900000001")
        self.auth = APIClient()
        self.auth.force_authenticate(self.user)
        self.category = CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе", google_type="cafe")
        task = mock.Mock(id="task-1")
        for name in ("fetch_google_competitors_task", "fetch_and_update_competitors_2gis"):
            p = mock.patch(f"{VIEWS}.{name}.delay", return_value=task)
            setattr(self, name, p.start())
            self.addCleanup(p.stop)

    def test_sync_endpoints_require_login(self):
        anon = APIClient()
        self.assertEqual(anon.post("/api/competitors/competitor/sync-2gis/", {"query": "kafe"},
                                   format="json").status_code, 401)
        self.assertEqual(anon.post("/api/competitors/competitor/sync-google/",
                                   {"lat": 41.3, "lng": 69.2, "category_id": self.category.id},
                                   format="json").status_code, 401)
        self.assertFalse(self.fetch_google_competitors_task.called)
        self.assertFalse(self.fetch_and_update_competitors_2gis.called)

    def test_google_hourly_limit(self):
        body = {"lat": 41.3, "lng": 69.2, "category_id": self.category.id}
        codes = [self.auth.post("/api/competitors/competitor/sync-google/", body, format="json").status_code
                 for _ in range(11)]
        self.assertEqual(codes[:10], [202] * 10)
        self.assertEqual(codes[10], 429)

    def test_analysis_requires_login(self):
        with mock.patch(f"{VIEWS}.fetch_and_save_nearby_competitors") as google:
            r = APIClient().get("/api/competitors/analysis/",
                                {"lat": 41.3, "long": 69.2, "radius": 300, "category_id": self.category.id})
        self.assertEqual(r.status_code, 401)
        self.assertFalse(google.called)

    def test_list_triggers_2gis_only_for_logged_in_users(self):
        params = {"category": "Kafe", "query": "hech narsa"}
        r = APIClient().get("/api/competitors/competitor/", params)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(self.fetch_and_update_competitors_2gis.called)

        r = self.auth.get("/api/competitors/competitor/", params)
        self.assertEqual(r.status_code, 202)
        self.assertTrue(self.fetch_and_update_competitors_2gis.called)
