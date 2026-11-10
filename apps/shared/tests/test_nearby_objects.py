"""shared.functions.get_nearby_objects."""
from decimal import Decimal

from django.test import TestCase

from apps.government_bodies.models import GovernmentBody
from apps.property.property_listing.models import PropertyListing
from apps.shared.functions import get_nearby_objects


class NearbyObjectsTests(TestCase):
    def body(self, name, lat, lng):
        return GovernmentBody.objects.create(name_uz=name, address="-", schedule="-", phone_number="-",
                                             director="-", latitude=lat, longitude=lng)

    def test_radius_and_order(self):
        self.body("2km", 41.3180, 69.2797)
        self.body("0.5km", 41.3045, 69.2797)
        self.body("20km", 41.4800, 69.2797)
        self.body("no coords", None, None)
        result = get_nearby_objects(41.3000, 69.2797, radius_km=5, model=GovernmentBody)
        self.assertEqual([b.name_uz for b in result], ["0.5km", "2km"])

    def test_decimal_coordinates(self):
        PropertyListing.objects.create(property_type="flat", title="Nearby", description="-", address="-",
                                       price=1, currency="USD", area_sq_m=1, rooms=1, floor=1,
                                       latitude=Decimal("41.300500"), longitude=Decimal("69.279700"))
        result = get_nearby_objects("41.3", "69.2797", model=PropertyListing)
        self.assertEqual([p.title for p in result], ["Nearby"])
