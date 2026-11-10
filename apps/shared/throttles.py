"""Rate limits for endpoints that spend money on external APIs.

Each provider has its own scope, so every endpoint that hits the same
provider draws from the same per-user budget. Rates live in
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].
"""
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle, UserRateThrottle


class AIThrottle(UserRateThrottle):
    scope = "ai"


class GoogleApiThrottle(UserRateThrottle):
    scope = "google"


class TwoGisApiThrottle(UserRateThrottle):
    scope = "twogis"


class PhoneNumberThrottle(SimpleRateThrottle):
    """Keyed by phone number: the logged-in user's, or phone_number in the body.

    An attacker targeting an account works against one fixed number, so this
    holds even when they rotate IPs.
    """

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            phone = request.user.phone_number
        else:
            phone = request.data.get("phone_number")
        if not phone:
            return None  # the serializer rejects the request anyway
        return self.cache_format % {"scope": self.scope, "ident": str(phone).strip().lower()}


class OTPSendThrottle(PhoneNumberThrottle):
    """How many codes may be sent to one number."""
    scope = "otp_send"


class OTPVerifyThrottle(PhoneNumberThrottle):
    """How many codes may be checked for one number (verify and reset share it)."""
    scope = "otp_verify"


class SignupThrottle(AnonRateThrottle):
    """Per client IP. Every signup uses a new number, so a phone key can't help here.

    The real client IP comes from X-Forwarded-For, so REST_FRAMEWORK's
    NUM_PROXIES must match the number of proxies in front of the app.
    """
    scope = "signup"


def allow_paid_call(throttle_class, request, view):
    """For endpoints that are public but may trigger a paid call as a side effect.

    Only authenticated users within their budget may trigger it; everyone else
    still gets the normal response, just without the external fetch.
    """
    if not request.user.is_authenticated:
        return False
    return throttle_class().allow_request(request, view)
