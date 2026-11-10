import secrets
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.models import BaseTimeModel
from apps.users.models.user_manager import UserManager



USER, ADMIN = ('user', 'admin')
NEW, CODE_VERIFIED, DONE = ('new', 'code_verified', 'done')

OTP_LENGTH = 6
OTP_MAX_ATTEMPTS = 5


class User(AbstractBaseUser, PermissionsMixin, BaseTimeModel):

    AUTH_STATUS = (
        (NEW, 'New'),
        (CODE_VERIFIED, 'Code verified'),
        (DONE, 'Done'),
    )

    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number

    def create_verify_code(self):
        from apps.users.models.user_confirmation import UserConfirmation
        if self.is_superuser:
            return None  # superuser uchun code yaratma

        code = f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"

        # Only the newest code is valid: otherwise every resend would add
        # another live code (and another set of attempts) to guess against.
        now = timezone.now()
        self.verify_codes.filter(is_confirmed=False, expiration_time__gt=now).update(expiration_time=now)

        UserConfirmation.objects.create(user=self, code=code)
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
