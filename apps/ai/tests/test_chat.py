"""POST /api/ai/chat/ (UniversalAIView): login required, 20 requests/hour. OpenAI is mocked."""
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.shared.testing import LOCMEM_CACHE
from apps.users.models.user import User

URL = "/api/ai/chat/"


@override_settings(CACHES=LOCMEM_CACHE)
class ChatAccessTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(phone_number="998900000001")
        patcher = mock.patch("apps.ai.views.chat_ai_view.BusinessAgent.ask_ai", return_value={"ok": True})
        self.ask_ai = patcher.start()
        self.addCleanup(patcher.stop)

    def test_anonymous_cannot_spend_openai(self):
        self.assertEqual(APIClient().post(URL, {"query": "cafe"}, format="json").status_code, 401)
        self.assertFalse(self.ask_ai.called)

    def test_networks_ai_query_is_protected_too(self):
        # A second endpoint that calls OpenAI; it used to be open to anyone.
        url = "/api/networks/cell-towers/ai_query/"
        with mock.patch("apps.networks.views.BusinessAgent.ask_ai", return_value={"ok": True}) as ask:
            self.assertEqual(APIClient().get(url, {"query": "cafe"}).status_code, 401)
            self.assertFalse(ask.called)
            client = APIClient()
            client.force_authenticate(self.user)
            self.assertEqual(client.get(url, {"query": "cafe"}).status_code, 200)

    def test_chat_and_ai_query_share_the_hourly_limit(self):
        client = APIClient()
        client.force_authenticate(self.user)
        with mock.patch("apps.networks.views.BusinessAgent.ask_ai", return_value={"ok": True}):
            for _ in range(20):
                client.post(URL, {"query": "cafe"}, format="json")
            self.assertEqual(client.get("/api/networks/cell-towers/ai_query/", {"query": "cafe"}).status_code, 429)

    def test_hourly_limit(self):
        client = APIClient()
        client.force_authenticate(self.user)
        codes = [client.post(URL, {"query": "cafe"}, format="json").status_code for _ in range(21)]
        self.assertEqual(codes[:20], [200] * 20)
        self.assertEqual(codes[20], 429)
        self.assertEqual(self.ask_ai.call_count, 20)
