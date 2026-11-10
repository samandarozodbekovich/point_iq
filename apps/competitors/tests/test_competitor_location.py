"""Competitor.location stays in step with latitude/longitude (CompetitorQuerySet, save, migration 0010)."""
import importlib

from django.apps import apps as django_apps
from django.contrib.gis.geos import Point
from django.test import TestCase

from apps.competitors.competitor.models import Competitor


def coords(c):
    c.refresh_from_db()
    return (round(c.location.y, 6), round(c.location.x, 6)) if c.location else None


class CompetitorLocationTests(TestCase):
    def test_bulk_create_fills_location(self):
        Competitor.objects.bulk_create([Competitor(name_uz="A", latitude=41.3, longitude=69.2),
                                        Competitor(name_uz="B")])
        self.assertEqual(coords(Competitor.objects.get(name_uz="A")), (41.3, 69.2))
        self.assertIsNone(Competitor.objects.get(name_uz="B").location)

    def test_bulk_update_follows_coordinates(self):
        c = Competitor.objects.create(name_uz="A", latitude=41.3, longitude=69.2)
        c.latitude, c.longitude = 41.35, 69.25
        Competitor.objects.bulk_update([c], ["latitude", "longitude"])
        self.assertEqual(coords(c), (41.35, 69.25))

    def test_save_clears_location_when_coordinates_removed(self):
        c = Competitor.objects.create(name_uz="A", latitude=41.3, longitude=69.2)
        c.latitude = c.longitude = None
        c.save()
        self.assertIsNone(coords(c))

    def test_save_with_update_fields(self):
        c = Competitor.objects.create(name_uz="A", latitude=41.3, longitude=69.2)
        c.latitude = 41.4
        c.save(update_fields=["latitude"])
        self.assertEqual(coords(c), (41.4, 69.2))

    def test_queryset_update(self):
        c = Competitor.objects.create(name_uz="A", latitude=41.3, longitude=69.2)
        Competitor.objects.filter(pk=c.pk).update(latitude=41.5, longitude=69.5)
        self.assertEqual(coords(c), (41.5, 69.5))
        with self.assertRaises(ValueError):
            Competitor.objects.filter(pk=c.pk).update(latitude=41.6)  # would desync

    def test_migration_repairs_existing_rows(self):
        missing = Competitor.objects.create(name_uz="no location", latitude=41.3, longitude=69.2)
        stale = Competitor.objects.create(name_uz="stale", latitude=None, longitude=None)
        # Simulate old data, bypassing the manager's own syncing.
        Competitor.objects.filter(pk=missing.pk).update(location=None)
        Competitor.objects.filter(pk=stale.pk).update(location=Point(69.0, 41.0, srid=4326))

        importlib.import_module("apps.competitors.migrations.0010_sync_location").sync(django_apps, None)

        self.assertEqual(coords(missing), (41.3, 69.2))
        self.assertIsNone(coords(stale))
