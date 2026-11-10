from django.db import models
from apps.shared.models import BaseTimeModel, SoftDeleteManager
from apps.users.models import User


class PropertyListing(BaseTimeModel):

    CURRENCY_CHOICES = (
        ('UZB',"Sum"),
        ('USD',"Dollar"),
        ("EUR",'Euro'),
    )

    owner = models.ForeignKey(User, on_delete=models.SET_NULL , null=True, blank=True)
    property_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    area_sq_m = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField()
    floor = models.IntegerField()
    total_floors = models.IntegerField(null=True, blank=True)
    year_built = models.IntegerField(null=True,blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    listing_url = models.TextField(null=True, blank=True)
    is_for_sale = models.BooleanField(default=False)
    is_for_rent = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()  # faqat o‘chirilmaganlar
    all_objects = models.Manager()

    class Meta:
        # For get_nearby_objects' bounding-box query.
        indexes = [models.Index(fields=['latitude', 'longitude'], name='listing_lat_lng_idx')]

    def __str__(self):
        return self.title
