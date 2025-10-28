import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.models import BaseTimeModel
from apps.users.models.user_manager import UserManager



USER, ADMIN = ('user', 'admin')
NEW, CODE_VERIFIED, DONE = ('new', 'code_verified', 'done')


class User(AbstractBaseUser, PermissionsMixin, BaseTimeModel):

    AUTH_STATUS = (
        (NEW, 'New'),
        (CODE_VERIFIED, 'Code verified'),
        (DONE, 'Done'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def create_verify_code(self):
        from apps.users.models.user_confirmation import UserConfirmation
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        UserConfirmation.objects.create(user=self, code=code)
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
