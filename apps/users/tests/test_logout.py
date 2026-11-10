"""POST logout/."""
from apps.users.tests.utils import API, PASSWORD, ApiTestCase, bearer, done_user


class LogoutTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = done_user()
        self.tokens = self.login(self.user.phone_number)

    def login(self, phone):
        return self.client.post(API + "login/", {"phone_number": phone, "password": PASSWORD}, format="json").data

    def logout(self, access, refresh):
        return bearer(access).post(API + "logout/", {"refresh": refresh}, format="json")

    def test_logout_blacklists_refresh_token(self):
        r = self.logout(self.tokens["access"], self.tokens["refresh"])
        self.assertEqual(r.status_code, 200, r.data)
        r = self.client.post(API + "login-refresh/", {"refresh": self.tokens["refresh"]}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_invalid_token_is_an_error(self):
        # Used to answer 200 with success: false.
        r = self.logout(self.tokens["access"], "not-a-token")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.data["success"])

    def test_cannot_log_out_another_user(self):
        other = done_user(phone="998907778899")
        other_tokens = self.login(other.phone_number)
        self.assertEqual(self.logout(self.tokens["access"], other_tokens["refresh"]).status_code, 400)
        r = self.client.post(API + "login-refresh/", {"refresh": other_tokens["refresh"]}, format="json")
        self.assertEqual(r.status_code, 200, "other user's session was ended")

    def test_requires_login(self):
        r = self.client.post(API + "logout/", {"refresh": self.tokens["refresh"]}, format="json")
        self.assertEqual(r.status_code, 401)
