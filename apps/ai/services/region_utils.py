from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="get_place_app")

def get_region_coordinates(region: str):

    if not region:
        return None
    try:
        loc = geolocator.geocode(region)
        if loc:
<<<<<<< HEAD
            return (loc.latitude, loc.longitude)
=======
            return loc.latitude, loc.longitude
>>>>>>> 7cb6155 (Initial clean commit)
    except:
        pass
    return None
