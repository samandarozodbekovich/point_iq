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
