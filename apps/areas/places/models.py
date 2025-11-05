import requests
from django.conf import settings
from django.db import models

from apps.areas.streets.models import Street
from apps.shared.models import BaseTimeModel

class Place(BaseTimeModel):
    street = models.ForeignKey(Street, on_delete=models.CASCADE, related_name="places")
    house_number = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['street', 'house_number']

    def __str__(self):
        return f"{self.house_number} ({self.street.name_uz})"

    @property
    def full_address(self):
        return f"{self.street.name_uz}, {self.street.area.name_uz}, {self.street.area.district.name_uz}, {self.street.area.city.name_uz}"

    def save(self, *args, **kwargs):
        # Agar latitude/longitude bo‘sh bo‘lsa — manzildan aniqlaymiz
        if not self.latitude or not self.longitude:
            address = f"{self.street} {self.house_number or ''}"
            lat, lon = self.get_coordinates_from_address(address)
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
        super().save(*args, **kwargs)

    def get_coordinates_from_address(self, address):
        """
        Yandex orqali koordinata olish
        """
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": settings.YANDEX_MAPS_API_KEY,
            "geocode": address,
            "format": "json",
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            lon, lat = pos.split(" ")
            return float(lat), float(lon)
        except Exception:
            return None, None
