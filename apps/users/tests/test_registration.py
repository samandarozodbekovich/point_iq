"""Signup -> verify -> change-info (POST signup/, POST verify/, PUT change-info/)."""
from django.utils import timezone

from apps.users.models.user import CODE_VERIFIED, DONE, NEW, OTP_LENGTH, User
from apps.users.models.user_confirmation import UserConfirmation
from apps.users.tests.utils import API, PASSWORD, ApiTestCase, bearer, latest_code, wrong_code

PHONE = "998901234567"


class RegistrationFlowTests(ApiTestCase):
    def signup(self, phone=PHONE):
        r = self.client.post(API + "signup/", {"phone_number": phone}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        return User.objects.get(phone_number=phone), r.data

    def change_info(self, access):
        return bearer(access).put(API + "change-info/", {
            "first_name": "Ali", "last_name": "Valiyev", "password": PASSWORD, "confirm_password": PASSWORD,
        }, format="json")

    def test_full_flow(self):
        user, tokens = self.signup()
        self.assertEqual(user.auth_status, NEW)
        code = latest_code(user)
        self.assertEqual(len(code), OTP_LENGTH)

        r = bearer(tokens["access"]).post(API + "verify/", {"code": code}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        user.refresh_from_db()
        self.assertEqual(user.auth_status, CODE_VERIFIED)

        r = self.change_info(r.data["access"])
        self.assertEqual(r.status_code, 200, r.data)
        user.refresh_from_db()
        self.assertEqual(user.auth_status, DONE)
        self.assertIn("access", r.data)

        r = self.client.post(API + "login/", {"phone_number": PHONE, "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 200, r.data)

    def test_cannot_finish_registration_without_verifying(self):
        # The original hole: change-info straight after signup gave a full account.
        user, tokens = self.signup()
        r = self.change_info(tokens["access"])
        self.assertEqual(r.status_code, 403)
        user.refresh_from_db()
        self.assertEqual(user.auth_status, NEW)

    def test_finished_account_cannot_reuse_change_info(self):
        user, tokens = self.signup()
        r = bearer(tokens["access"]).post(API + "verify/", {"code": latest_code(user)}, format="json")
        access = self.change_info(r.data["access"]).data["access"]
        self.assertEqual(self.change_info(access).status_code, 403)

    def test_signup_token_dies_once_password_is_set(self):
        user, tokens = self.signup()
        r = bearer(tokens["access"]).post(API + "verify/", {"code": latest_code(user)}, format="json")
        verify_access = r.data["access"]
        new_access = self.change_info(verify_access).data["access"]

        self.assertEqual(bearer(verify_access).post(API + "logout/", {"refresh": "x"}, format="json").status_code, 401)
        self.assertNotEqual(bearer(new_access).post(API + "logout/", {"refresh": "x"}, format="json").status_code, 401)

    def test_login_refused_until_done(self):
        user, _ = self.signup()
        user.set_password(PASSWORD)
        user.save()
        r = self.client.post(API + "login/", {"phone_number": PHONE, "password": PASSWORD}, format="json")
        self.assertEqual(r.status_code, 403)


class VerifyCodeTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        r = self.client.post(API + "signup/", {"phone_number": PHONE}, format="json")
        self.user = User.objects.get(phone_number=PHONE)
        self.api = bearer(r.data["access"])

    def verify(self, code):
        return self.api.post(API + "verify/", {"code": code}, format="json")

    def test_locks_after_five_wrong_attempts(self):
        code = latest_code(self.user)
        for _ in range(5):
            self.assertEqual(self.verify(wrong_code(code)).status_code, 400)
        r = self.verify(code)
        self.assertEqual(r.status_code, 400)
        self.assertIn("Too many attempts", str(r.data))
        self.user.refresh_from_db()
        self.assertEqual(self.user.auth_status, NEW)

    def test_only_newest_code_is_valid(self):
        old = latest_code(self.user)
        self.user.create_verify_code()
        self.assertEqual(self.verify(old).status_code, 400)
        self.assertEqual(self.verify(latest_code(self.user)).status_code, 200)

    def test_expired_code_rejected(self):
        code = latest_code(self.user)
        UserConfirmation.objects.filter(user=self.user).update(expiration_time=timezone.now())
        self.assertEqual(self.verify(code).status_code, 400)

    def test_code_cannot_be_reused(self):
        code = latest_code(self.user)
        self.assertEqual(self.verify(code).status_code, 200)
        self.assertEqual(self.verify(code).status_code, 400)

    def test_wrong_length_rejected_without_spending_an_attempt(self):
        self.assertEqual(self.verify("12").status_code, 400)
        self.assertEqual(UserConfirmation.objects.get(user=self.user).attempts, 0)

    def test_verify_requires_login(self):
        self.assertEqual(self.client.post(API + "verify/", {"code": "123456"}, format="json").status_code, 401)
