"""Password reset: POST forgot-password/ then PUT reset-password/."""
from apps.users.models.user import User
from apps.users.models.user_confirmation import UserConfirmation
from apps.users.tests.utils import API, PASSWORD, ApiTestCase, bearer, done_user, latest_code, wrong_code

NEW_PASSWORD = "An0ther-Strong-Pass!"


class PasswordResetTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = done_user()
        self.phone = self.user.phone_number

    def forgot(self, phone):
        return self.client.post(API + "forgot-password/", {"phone_number": phone}, format="json")

    def reset(self, code, password=NEW_PASSWORD, phone=None):
        return self.client.put(API + "reset-password/", {
            "phone_number": phone or self.phone, "code": code,
            "password": password, "confirm_password": password,
        }, format="json")

    def login(self, password):
        return self.client.post(API + "login/", {"phone_number": self.phone, "password": password}, format="json")

    def test_full_reset(self):
        self.assertEqual(self.forgot(self.phone).status_code, 200)
        r = self.reset(latest_code(self.user))
        self.assertEqual(r.status_code, 200, r.data)
        self.assertIn("access", r.data)
        self.assertEqual(self.login(NEW_PASSWORD).status_code, 200)
        self.assertNotEqual(self.login(PASSWORD).status_code, 200)

    def test_reset_requires_the_code(self):
        # reset-password used to accept no proof of phone ownership at all.
        self.forgot(self.phone)
        self.assertEqual(self.reset(wrong_code(latest_code(self.user))).status_code, 400)
        self.assertEqual(self.login(PASSWORD).status_code, 200)

    def test_locks_after_five_wrong_codes(self):
        self.forgot(self.phone)
        code = latest_code(self.user)
        for _ in range(5):
            self.reset(wrong_code(code))
        r = self.reset(code)
        self.assertEqual(r.status_code, 400)
        self.assertIn("Too many attempts", str(r.data))

    def test_weak_password_does_not_spend_an_attempt(self):
        self.forgot(self.phone)
        self.assertEqual(self.reset(latest_code(self.user), password="12345678").status_code, 400)
        self.assertEqual(UserConfirmation.objects.filter(user=self.user).order_by("-id").first().attempts, 0)

    def test_unknown_number_looks_like_a_known_one(self):
        known, unknown = self.forgot(self.phone), self.forgot("998909999999")
        self.assertEqual((known.status_code, known.data), (unknown.status_code, unknown.data))
        self.assertFalse(User.objects.filter(phone_number="998909999999").exists())

        r = self.reset("123456", phone="998909999999")
        self.assertEqual(r.status_code, 400)
        self.assertIn("Invalid or expired", str(r.data))

    def test_unfinished_account_gets_no_code(self):
        pending = User.objects.create_user(phone_number="998905556677")  # still NEW
        codes_before = UserConfirmation.objects.filter(user=pending).count()
        self.assertEqual(self.forgot(pending.phone_number).status_code, 200)
        self.assertEqual(UserConfirmation.objects.filter(user=pending).count(), codes_before)

    def test_reset_ends_existing_sessions(self):
        old = self.login(PASSWORD).data
        self.forgot(self.phone)
        self.reset(latest_code(self.user))

        # Old access token: rejected at once (CHECK_REVOKE_TOKEN).
        self.assertEqual(bearer(old["access"]).post(API + "logout/", {"refresh": old["refresh"]},
                                                    format="json").status_code, 401)
        # Old refresh token: blacklisted.
        r = self.client.post(API + "login-refresh/", {"refresh": old["refresh"]}, format="json")
        self.assertEqual(r.status_code, 401)
