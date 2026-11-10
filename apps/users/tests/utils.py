"""Helpers for the users tests. Not collected as tests (name doesn't start with test)."""
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.shared.testing import LOCMEM_CACHE
from apps.users.models.user import DONE, User
from apps.users.models.user_confirmation import UserConfirmation

API = "/api/users/"
PASSWORD = "Str0ng-Pass-2026!"


def latest_code(user):
    """The code that was sent; read from the database since SMS is not wired."""
    return UserConfirmation.objects.filter(user=user).order_by("-id").first().code


def wrong_code(code):
    return "0" * len(code) if code != "0" * len(code) else "1" * len(code)


def done_user(phone="998901112233", password=PASSWORD):
    """A user who finished registration and can log in."""
    user = User.objects.create_user(phone_number=phone, password=password)
    user.auth_status = DONE
    user.save()
    return user


def bearer(access):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


@override_settings(CACHES=LOCMEM_CACHE)
class ApiTestCase(TestCase):
    """Fresh throttle counters for every test."""

    def setUp(self):
        cache.clear()
        self.client = APIClient()
