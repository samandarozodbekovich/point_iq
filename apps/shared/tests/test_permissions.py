"""Write permissions of the shared viewsets (BaseModelViewSet, BaseDeletedItemsViewSet)."""
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.government_bodies.models import GovernmentBody
from apps.property.property_images.models import PropertyImage
from apps.property.property_listing.models import PropertyListing
from apps.shared.testing import LOCMEM_CACHE
from apps.users.models.user import User

# 1x1 transparent GIF
GIF = (b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
       b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")


def client_for(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


@override_settings(CACHES=LOCMEM_CACHE)
class BaseModelViewSetPermissionTests(TestCase):
    """Reads are public, every write is admin-only (GovernmentBodyViewSet as the example)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone_number="998900000001")
        cls.admin = User.objects.create_user(phone_number="998900000002", is_staff=True)
        cls.body = GovernmentBody.objects.create(name_uz="Hokimiyat", address="-", schedule="-",
                                                 phone_number="-", director="-")

    def test_bulk_create_was_open_to_anonymous(self):
        payload = [{"name_uz": "X", "address": "-", "schedule": "-", "phone_number": "-", "director": "-"}]
        self.assertEqual(client_for().post("/api/government/create/", payload, format="json").status_code, 401)
        self.assertEqual(client_for(self.user).post("/api/government/create/", payload, format="json").status_code, 403)
        self.assertEqual(GovernmentBody.objects.count(), 1)

    def test_reads_are_public(self):
        self.assertEqual(client_for().get("/api/government/").status_code, 200)
        self.assertEqual(client_for().get(f"/api/government/{self.body.pk}/").status_code, 200)

    def test_delete_admin_only_and_works(self):
        url = f"/api/government/{self.body.pk}/"
        self.assertEqual(client_for(self.user).delete(url).status_code, 403)
        # Used to answer 404 for everyone: get_queryset returned none() for destroy.
        self.assertEqual(client_for(self.admin).delete(url).status_code, 204)
        self.assertFalse(GovernmentBody.objects.exists())


@override_settings(CACHES=LOCMEM_CACHE)
class OwnedResourcePermissionTests(TestCase):
    """Property listings and their images belong to the listing owner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media = tempfile.mkdtemp()
        cls.media_override = override_settings(MEDIA_ROOT=cls.media)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.media, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(phone_number="998900000011")
        cls.other = User.objects.create_user(phone_number="998900000012")
        cls.listing = PropertyListing.objects.create(
            owner=cls.owner, property_type="flat", title="Uy", description="-", address="Chilonzor",
            price=1, currency="USD", area_sq_m=1, rooms=1, floor=1)

    def listing_payload(self):
        return {"property_type": "flat", "title": "New listing", "description": "-", "address": "-", "price": "1",
                "currency": "USD", "area_sq_m": "1", "rooms": 1, "floor": 1}

    def image(self):
        return SimpleUploadedFile("a.gif", GIF, content_type="image/gif")

    def test_anonymous_create_is_401_not_500(self):
        r = client_for().post("/api/property/", self.listing_payload(), format="json")
        self.assertEqual(r.status_code, 401)

    def test_create_sets_owner(self):
        r = client_for(self.other).post("/api/property/", self.listing_payload(), format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(PropertyListing.objects.get(title="New listing").owner, self.other)

    def test_only_owner_edits_listing(self):
        url = f"/api/property/{self.listing.pk}/"
        self.assertEqual(client_for(self.other).patch(url, {"title": "Meniki"}, format="json").status_code, 403)
        self.assertEqual(client_for(self.owner).patch(url, {"title": "Yangilandi"}, format="json").status_code, 200)

    def test_images_only_on_own_listing(self):
        r = client_for(self.other).post("/api/property/images/", {"property": self.listing.pk, "image": self.image()},
                                        format="multipart")
        self.assertEqual(r.status_code, 403)
        r = client_for(self.owner).post("/api/property/images/", {"property": self.listing.pk, "image": self.image()},
                                        format="multipart")
        # Used to fail with a 500 for everyone: PropertyImage has no owner field.
        self.assertEqual(r.status_code, 201, r.data)

    def test_image_edit_checks_listing_owner(self):
        img = PropertyImage.objects.create(property=self.listing, image=self.image())
        url = f"/api/property/images/{img.pk}/"
        self.assertEqual(client_for(self.other).delete(url).status_code, 403)

    def test_image_bulk_writes_admin_only(self):
        self.assertEqual(client_for(self.owner).post("/api/property/images/create/", [], format="json").status_code, 403)
