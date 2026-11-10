"""Rate limits for endpoints that spend money on external APIs.

Each provider has its own scope, so every endpoint that hits the same
provider draws from the same per-user budget. Rates live in
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].
"""
from rest_framework.throttling import UserRateThrottle


class AIThrottle(UserRateThrottle):
    scope = "ai"


class GoogleApiThrottle(UserRateThrottle):
    scope = "google"


class TwoGisApiThrottle(UserRateThrottle):
    scope = "twogis"


def allow_paid_call(throttle_class, request, view):
    """For endpoints that are public but may trigger a paid call as a side effect.

    Only authenticated users within their budget may trigger it; everyone else
    still gets the normal response, just without the external fetch.
    """
    if not request.user.is_authenticated:
        return False
    return throttle_class().allow_request(request, view)
