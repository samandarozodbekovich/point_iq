"""competitors.utils.search_place_2gis (2GIS import). Network is mocked; database writes are real."""
import importlib
from unittest import mock

from django.test import TestCase

from apps.competitors.competitor.models import Competitor
from apps.competitors.competitor_categories.models import CompetitorCategory

# The package __init__ re-exports a function with the module's name, so
# `from ... import search_place_2gis` would give the function.
s = importlib.import_module("apps.competitors.utils.search_place_2gis")


class TwoGisSearchTests(TestCase):
    def setUp(self):
        CompetitorCategory.objects.create(name_uz="Kafe", name_ru="Кафе")

    def page(self, ids, total):
        items = [{"id": f"{i}_x", "name": f"Kafe {i}", "full_name": "Tashkent", "purpose_name": "Кафе",
                  "point": {"lat": 41.3, "lon": 69.2}} for i in ids]
        resp = mock.Mock(status_code=200)
        resp.json.return_value = {"result": {"items": items, "total": total}}
        return resp

    def test_stops_at_total_requests_fields_and_skips_byid(self):
        pages = [self.page(range(0, 10), 15), self.page(range(10, 15), 15), self.page(range(99, 109), 15)]
        with mock.patch.object(s.requests, "get", side_effect=pages) as get, \
             mock.patch.object(s, "fetch_item_details") as byid, mock.patch.object(s.time, "sleep"):
            created = s.search_place_2gis("kafe")
        self.assertEqual(get.call_count, 2, "kept paging after reaching total")
        self.assertIn("fields", get.call_args.kwargs["params"])
        self.assertFalse(byid.called)
        self.assertEqual(created, 15)

    def test_second_import_creates_no_duplicates(self):
        # The ids were compared as int against a TextField, so this re-created rows.
        for _ in range(2):
            with mock.patch.object(s.requests, "get", side_effect=[self.page(range(0, 10), 10)]), \
                 mock.patch.object(s.time, "sleep"):
                s.search_place_2gis("kafe")
        self.assertEqual(Competitor.objects.count(), 10)

    def test_page_cap(self):
        endless = (self.page(range(n * 10, n * 10 + 10), 10_000) for n in range(1000))
        with mock.patch.object(s.requests, "get", side_effect=endless) as get, mock.patch.object(s.time, "sleep"):
            s.search_place_2gis("kafe")
        self.assertEqual(get.call_count, s.MAX_PAGES)
