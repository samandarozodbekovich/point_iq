import importlib
from unittest import mock
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from hitcount.models import HitCount
from rest_framework.test import APIClient

from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.competitors.competitor_review.models import CompetitorReview
from apps.users.models.user import User

LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(CACHES=LOCMEM)
class CompetitorListQueryCountTests(TestCase):
    """The competitor list must cost the same number of queries for any size."""

    @classmethod
    def setUpTestData(cls):
        cls.category = CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе", name_cyr="Кафе")
        cls.users = [User.objects.create_user(phone_number=f"99890000000{i}") for i in range(3)]

    def make_competitors(self, n):
        for i in range(n):
            c = Competitor.objects.create(
                category=self.category, name_uz=f"Kafe {i}", name_ru=f"Кафе {i}", name_cyr="",
                latitude=41.3 + i / 1000, longitude=69.2,
            )
            for u, rating in zip(self.users, (3, 4, 5)):
                CompetitorReview.objects.create(competitor=c, user=u, rating=rating)
            HitCount.objects.get_for_object(c)

    def count_list_queries(self):
        with CaptureQueriesContext(connection) as ctx:
            response = APIClient().get("/api/competitors/competitor/", {"category": "Kafe"})
        self.assertEqual(response.status_code, 200)
        return len(ctx.captured_queries), response.data

    def test_query_count_does_not_grow_with_rows(self):
        self.make_competitors(3)
        small, _ = self.count_list_queries()
        self.make_competitors(12)
        large, data = self.count_list_queries()

        self.assertEqual(data["count"], 15)
        self.assertEqual(small, large, f"3 rows: {small} queries, 15 rows: {large} queries")
        # 15 rows used to take 108 queries. Now: count, competitors+category,
        # reviews+users, hit counts, plus the exists() check.
        self.assertLessEqual(large, 5)

    def test_list_does_not_write(self):
        c = Competitor.objects.create(category=self.category, name_uz="Yangi", name_ru="Новый", name_cyr="")
        before = HitCount.objects.count()
        _, data = self.count_list_queries()
        self.assertEqual(HitCount.objects.count(), before, "GET list created HitCount rows")
        self.assertEqual([r["hits"] for r in data["results"] if r["id"] == c.id], [0])

    def test_migration_recomputes_stale_stats(self):
        import importlib
        from django.apps import apps as django_apps
        self.make_competitors(2)
        Competitor.objects.update(average_rating=None, review_count=0)  # state before the fix
        migration = importlib.import_module("apps.competitors.migrations.0009_recompute_review_stats")
        migration.recompute(django_apps, None)
        self.assertEqual(set(Competitor.objects.values_list("average_rating", "review_count")), {(4.0, 3)})

    def test_rating_and_count_come_from_reviews(self):
        self.make_competitors(1)
        _, data = self.count_list_queries()
        row = data["results"][0]
        self.assertEqual(row["average_rating"], 4.0)
        self.assertEqual(row["review_count"], 3)
        self.assertEqual(len(row["reviews"]), 3)


@override_settings(CACHES=LOCMEM)
class CompetitorPaginationTests(TestCase):
    def test_list_is_paginated(self):
        cat = CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")
        Competitor.objects.bulk_create(
            [Competitor(category=cat, name_uz=f"K{i}", name_ru="К") for i in range(60)])
        client = APIClient()
        first = client.get("/api/competitors/competitor/", {"category": "Kafe"}).data
        self.assertEqual((first["status"], first["count"], len(first["results"])), ("success", 60, 50))
        self.assertIsNotNone(first["next"])
        second = client.get(first["next"]).data
        self.assertEqual(len(second["results"]), 10)
        self.assertIsNone(second["next"])
        ids = [r["id"] for r in first["results"] + second["results"]]
        self.assertEqual(len(set(ids)), 60, "pages overlap or skip rows")


class TwoGisSearchTests(TestCase):
    """Network is mocked; the database writes are real."""

    def page(self, ids, total):
        items = [{"id": f"{i}_x", "name": f"Kafe {i}", "full_name": "Toshkent", "purpose_name": "Кафе",
                  "point": {"lat": 41.3, "lon": 69.2}} for i in ids]
        resp = mock.Mock(status_code=200)
        resp.json.return_value = {"result": {"items": items, "total": total}}
        return resp

    def test_stops_at_total_requests_fields_and_skips_byid(self):
        s = importlib.import_module("apps.competitors.utils.search_place_2gis")
        CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")
        pages = [self.page(range(0, 10), 15), self.page(range(10, 15), 15), self.page(range(99, 109), 15)]
        with mock.patch.object(s.requests, "get", side_effect=pages) as get, \
             mock.patch.object(s, "fetch_item_details") as byid, mock.patch.object(s.time, "sleep"):
            created = s.search_place_2gis("kafe")
        self.assertEqual(get.call_count, 2, "kept paging after reaching total")
        self.assertIn("fields", get.call_args.kwargs["params"])
        self.assertFalse(byid.called)
        self.assertEqual(created, 15)

        # Same results again: nothing new (string ids now match the stored ones).
        with mock.patch.object(s.requests, "get", side_effect=[self.page(range(0, 10), 10)]), \
             mock.patch.object(s.time, "sleep"):
            self.assertEqual(s.search_place_2gis("kafe"), 0)
        self.assertEqual(Competitor.objects.count(), 15)

    def test_page_cap(self):
        s = importlib.import_module("apps.competitors.utils.search_place_2gis")
        CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")
        endless = (self.page(range(n * 10, n * 10 + 10), 10_000) for n in range(1000))
        with mock.patch.object(s.requests, "get", side_effect=endless) as get, mock.patch.object(s.time, "sleep"):
            s.search_place_2gis("kafe")
        self.assertEqual(get.call_count, s.MAX_PAGES)
