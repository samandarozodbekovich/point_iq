"""Code sending and its limits: POST resend-code/, GET get-new-verification/, POST signup/."""
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from apps.users.models.user import User
from apps.users.models.user_confirmation import UserConfirmation
from apps.users.tests.utils import API, ApiTestCase, bearer, latest_code

PHONE = "998901234567"


class GetNewVerificationTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        r = self.client.post(API + "signup/", {"phone_number": PHONE}, format="json")
        self.user = User.objects.get(phone_number=PHONE)
        self.api = bearer(r.data["access"])

    def test_code_is_not_in_the_response(self):
        # It used to return {"code": ...}, skipping phone verification.
        UserConfirmation.objects.filter(user=self.user).update(expiration_time=timezone.now())
        r = self.api.get(API + "get-new-verification/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertNotIn(latest_code(self.user), str(r.data))
        self.assertNotIn("code", r.data)

    def test_refused_while_a_code_is_still_live(self):
        self.assertEqual(self.api.get(API + "get-new-verification/").status_code, 400)

    def test_requires_login(self):
        self.assertEqual(self.client.get(API + "get-new-verification/").status_code, 401)


class OtpThrottleTests(ApiTestCase):
    def test_resend_limited_per_phone(self):
        User.objects.create_user(phone_number=PHONE)
        codes = [self.client.post(API + "resend-code/", {"phone_number": PHONE}, format="json").status_code
                 for _ in range(6)]
        self.assertEqual(codes[:5], [200] * 5)
        self.assertEqual(codes[5], 429)
        # Spaces don't make it a new number.
        r = self.client.post(API + "resend-code/", {"phone_number": f" {PHONE} "}, format="json")
        self.assertEqual(r.status_code, 429)

    def test_verify_limited_per_phone(self):
        r = self.client.post(API + "signup/", {"phone_number": PHONE}, format="json")
        api = bearer(r.data["access"])
        user = User.objects.get(phone_number=PHONE)
        statuses = []
        for _ in range(11):
            user.create_verify_code()  # fresh code each time, so only the throttle can stop it
            statuses.append(api.post(API + "verify/", {"code": "000000"}, format="json").status_code)
        self.assertNotIn(429, statuses[:10])
        self.assertEqual(statuses[10], 429)

    # Pinned here so the test doesn't depend on NUM_PROXIES in .env.
    @override_settings(REST_FRAMEWORK={**settings.REST_FRAMEWORK, "NUM_PROXIES": 1})
    def test_signup_limited_per_client_ip(self):
        def signup(n, ip):
            return self.client.post(API + "signup/", {"phone_number": f"99890000{n:04d}"}, format="json",
                                    HTTP_X_FORWARDED_FOR=ip).status_code
        self.assertEqual([signup(i, "1.1.1.1") for i in range(10)], [201] * 10)
        self.assertEqual(signup(10, "1.1.1.1"), 429)
        self.assertEqual(signup(11, "2.2.2.2"), 201)
        # A forged first entry doesn't help: the proxy's entry (last) is used.
        self.assertEqual(signup(12, "9.9.9.9, 1.1.1.1"), 429)
