import secrets

from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.users.models.user import OTP_MAX_ATTEMPTS
from apps.users.models.user_confirmation import UserConfirmation

INVALID_CODE_MESSAGE = "Invalid or expired verification code."


def _error(message):
    return ValidationError({"success": False, "message": message})


def invalid_code_error():
    return _error(INVALID_CODE_MESSAGE)


def consume_code(user, code):
    """Check `code` against the user's latest live OTP and mark it used.

    Raises ValidationError on a wrong, expired or exhausted code. Every call
    spends one attempt; after OTP_MAX_ATTEMPTS the code is dead and the user
    must request a new one.

    The attempt counter relies on autocommit: if ATOMIC_REQUESTS is ever
    enabled, DRF rolls back failed requests and the counter would never grow.
    """
    confirmation = user.verify_codes.filter(
        expiration_time__gte=timezone.now(),
        is_confirmed=False,
    ).order_by('-id').first()
    if confirmation is None:
        raise invalid_code_error()

    # Reserve an attempt in one UPDATE before comparing, so parallel
    # requests cannot squeeze in more than OTP_MAX_ATTEMPTS guesses.
    reserved = UserConfirmation.objects.filter(
        pk=confirmation.pk, attempts__lt=OTP_MAX_ATTEMPTS
    ).update(attempts=F('attempts') + 1)
    if not reserved:
        raise _error("Too many attempts. Request a new code.")

    if not secrets.compare_digest(confirmation.code, str(code)):
        raise invalid_code_error()

    confirmed = UserConfirmation.objects.filter(
        pk=confirmation.pk, is_confirmed=False
    ).update(is_confirmed=True)
    if not confirmed:
        raise invalid_code_error()
