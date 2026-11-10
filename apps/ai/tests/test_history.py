"""GET /api/ai/history/ and /api/ai/history/<pk>/."""
from django.test import TestCase
from rest_framework.test import APIClient

from apps.ai.models import QueryHistory
from apps.users.models.user import User


class HistoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone_number="998900000001")
        cls.other = User.objects.create_user(phone_number="998900000002")
        cls.mine = [QueryHistory.objects.create(user=cls.user, user_query=f"q{i}", status="done") for i in range(3)]
        cls.theirs = QueryHistory.objects.create(user=cls.other, user_query="secret", status="done")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_returns_own_entries_newest_first(self):
        r = self.client.get("/api/ai/history/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([e["id"] for e in r.data], [h.id for h in reversed(self.mine)])

    def test_detail_returns_one_entry(self):
        # Used to return the whole list (ListAPIView.get won the MRO).
        r = self.client.get(f"/api/ai/history/{self.mine[0].id}/")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.data, dict)
        self.assertEqual(r.data["id"], self.mine[0].id)

    def test_cannot_read_another_users_entry(self):
        self.assertEqual(self.client.get(f"/api/ai/history/{self.theirs.id}/").status_code, 404)

    def test_requires_login(self):
        self.assertEqual(APIClient().get("/api/ai/history/").status_code, 401)
