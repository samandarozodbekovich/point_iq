from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="get_place_app")

def get_region_coordinates(region: str):

    if not region:
        return None
    try:
        loc = geolocator.geocode(region)
        if loc:
            return (loc.latitude, loc.longitude)
    except:
        pass
    return None
