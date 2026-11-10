"""Migration 0009_recompute_review_stats."""
import importlib

from django.apps import apps as django_apps
from django.test import TestCase

from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory
from apps.competitors.competitor_review.models import CompetitorReview
from apps.users.models.user import User


class RecomputeReviewStatsTests(TestCase):
    def test_recomputes_stale_stats(self):
        cat = CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")
        users = [User.objects.create_user(phone_number=f"99891000000{i}") for i in range(3)]
        for i in range(2):
            c = Competitor.objects.create(category=cat, name_uz=f"K{i}", name_ru="К")
            for u, rating in zip(users, (3, 4, 5)):
                CompetitorReview.objects.create(competitor=c, user=u, rating=rating)
        Competitor.objects.update(average_rating=None, review_count=0)  # state before the fix

        migration = importlib.import_module("apps.competitors.migrations.0009_recompute_review_stats")
        migration.recompute(django_apps, None)

        self.assertEqual(set(Competitor.objects.values_list("average_rating", "review_count")), {(4.0, 3)})
