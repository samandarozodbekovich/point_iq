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


def parse_lat_lng(query_params):
    """Read lat/lng from query params as floats; None if missing or invalid."""
    try:
        lat = float(query_params.get('lat'))
        lng = float(query_params.get('lng'))
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None
    return lat, lng


KM_PER_DEGREE_LAT = 111.32


def get_nearby_objects(center_lat, center_lon, radius_km=5, model=None):
    """Objects of `model` within radius_km, nearest first.

    The database narrows rows to the bounding box around the circle (using
    the latitude/longitude index); the exact distance is computed only for
    those. This used to load the whole table into Python.
    """
    center_lat, center_lon = float(center_lat), float(center_lon)
    d_lat = radius_km / KM_PER_DEGREE_LAT
    d_lon = radius_km / (KM_PER_DEGREE_LAT * max(cos(radians(center_lat)), 0.01))

    candidates = model.objects.filter(
        latitude__range=(center_lat - d_lat, center_lat + d_lat),
        longitude__range=(center_lon - d_lon, center_lon + d_lon),
    )
    nearby = []
    for obj in candidates:
        distance = haversine(center_lat, center_lon, float(obj.latitude), float(obj.longitude))
        if distance <= radius_km:
            nearby.append((distance, obj))
    nearby.sort(key=lambda pair: pair[0])
    return [obj for _, obj in nearby]

def hit_count(request, hitcount):
    """Count one view per IP.

    The uniqueness check looks at Hit rows, so a Hit has to be recorded:
    calling hitcount.increase() alone left no Hit, every request from the
    same IP passed the check, and each one was counted. Hit.save() itself
    increments the counter on creation.
    """
    # Imported here: this module is imported by District's models module,
    # and pulling another app's models in at that point depends on load order.
    from hitcount.models import Hit

    ip = get_ip(request)
    if hitcount.hit_set.filter(ip=ip).exists():
        return

    user = getattr(request, 'user', None)
    session = getattr(request, 'session', None)
    Hit(
        hitcount=hitcount,
        ip=ip,
        session=(session.session_key if session else None) or '',
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        user=user if user is not None and user.is_authenticated else None,
    ).save()
