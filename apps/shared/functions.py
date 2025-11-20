from math import radians, cos, sin, asin, sqrt
from hitcount.utils import get_ip


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
