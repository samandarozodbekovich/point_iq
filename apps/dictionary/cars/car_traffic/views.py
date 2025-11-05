from django.conf import settings
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import logging

logger = logging.getLogger(__name__)

class MapConfigView(APIView):
    """
    Frontend uchun Yandex xarita sozlamalarini yuboradi.
    """
    def get(self, request):
        return Response({
            "apikey": getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
            "center": getattr(settings, 'YANDEX_MAP_CENTER', [41.311081, 69.240562]),  # Toshkent
            "zoom": getattr(settings, 'YANDEX_MAP_ZOOM', 12)
        })


class MapPageView(TemplateView):
    """
    Xarita sahifasini render qiladi (traffic-demo.html)
    """
    template_name = "traffic-demo.html"


class GeocodeView(APIView):
    """
    Yandex Geocoder API orqali manzilni koordinatalarga aylantiradi.
    """
    def get(self, request):
        q = request.query_params.get('q')
        if not q:
            return Response({"detail": "Missing query parameter 'q'."},
                            status=status.HTTP_400_BAD_REQUEST)

        api_key = getattr(settings, 'YANDEX_MAPS_API_KEY', '')
        if not api_key:
            return Response({"detail": "YANDEX_MAPS_API_KEY not found in settings"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        geocode_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": api_key,
            "format": "json",
            "geocode": q,
            "results": 1
        }

        try:
            resp = requests.get(geocode_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            members = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
            if not members:
                return Response({"detail": "No results found for given query."},
                                status=status.HTTP_404_NOT_FOUND)

            geo_object = members[0]['GeoObject']
            pos = geo_object['Point']['pos']  # "lon lat"
            lon, lat = map(float, pos.split())

            return Response({
                "coords": [lat, lon],
                "name": geo_object.get('name', q)
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"Yandex Geocode API request failed: {e}")
            return Response({"detail": "External API request failed", "error": str(e)},
                            status=status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            logger.exception("Unexpected error in GeocodeView")
            return Response({"detail": "Internal server error", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
