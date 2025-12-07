from math import radians, cos, sin, asin, sqrt

from django.db import transaction
from hitcount.utils import get_ip
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


def haversine(lat1, lon1, lat2, lon2):
    """count distance in km between two points"""
    R = 6371
    if not all([lat1, lon1, lat2, lon2]):
        return 9999
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def get_nearby_objects(center_lat, center_lon, radius_km=5, model=None):
    nearby_objs = []
    for object in model.objects.all():
        if not object.latitude or not object.longitude:
            continue
        distance = haversine(center_lat, center_lon, object.latitude, object.longitude)
        if distance <= radius_km:
            nearby_objs.append(object)
    return nearby_objs

def hit_count(request, hitcount):
    ip = get_ip(request)

    if not hitcount.hits:
        hitcount.hits = 0

    if not hitcount.hit_set.filter(ip=ip).exists():
        hitcount.increase()


@action(methods=['post'], detail=False, url_path='bulk-create')
def create(request, self, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    model = self.get_queryset().model

    all_objects = []
    created_objects = []

    with transaction.atomic():
        for item in serializer.validated_data:
            for li in self.get_lang_data(item):
                obj = model(**li)
                all_objects.append(obj)

        if all_objects:
            model.objects.bulk_create(all_objects, ignore_conflicts=True)
            created_objects = all_objects

    return Response(self.get_serializer(created_objects, many=True).data, status=status.HTTP_201_CREATED)


def point_in_polygon(lat, lon, polygon_coords):
    """
    Berilgan nuqta polygon ichida bo'lsa True qaytaradi
    """
    x, y = lon, lat
    n = len(polygon_coords)
    inside = False

    p1x, p1y = polygon_coords[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon_coords[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside
