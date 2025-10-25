import random
from apps.shared.models import BaseTimeModel
from django.db import models

USER, ADMIN = ('user', 'admin')

class User(BaseTimeModel):

    USER_ROLES = (
        (ADMIN, ADMIN),
        (USER, USER),
    )

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default=USER)
    is_active = models.BooleanField(default=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        # UserConfirmation.objects.create(
        #     user=self,
        #     verify_type=verify_type,
        #     code=code
        # )
        return code


# class UserConfirmation(BaseNameModel, BaseTimeModel):
#     TYPE_CHOICES = (
#         (VIA_EMAIL, VIA_EMAIL),
#         (VIA_PHONE, VIA_PHONE),
#     )
#
#     code = models.CharField(max_length=6)
#     verify_type = models.CharField(max_length=31, choices=TYPE_CHOICES)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verify_codes')
#     expiration_time = models.DateTimeField(null=True, blank=True)
#     is_confirmed = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f"{self.user} - {self.verify_type}"
#
#     def save(self, *args, **kwargs):
#         if self.verify_type == VIA_EMAIL:
#             self.expiration_time = datetime.now() + timedelta(minutes=5)
#         else:
#             self.expiration_time = datetime.now() + timedelta(minutes=2)
#         super().save(*args, **kwargs)



class SearchQuery(BaseTimeModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    user_query = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_miles = models.DecimalField(max_digits=5, decimal_places=2)
    filters = models.JSONField(null=True, blank=True)
