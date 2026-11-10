from django.db import connection


def get_road_traffic_multiplier(lat, lon):

    TRAFFIC_WEIGHTS = {
        'trunk': 1.0,
        'primary': 0.9,
        'secondary': 0.7,
        'tertiary': 0.5,
        'residential': 0.3,
        'service': 0.1
    }
    query = """
        SELECT highway
        FROM planet_osm_line
        WHERE highway IS NOT NULL
        ORDER BY way <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [lon, lat])
        row = cursor.fetchone()

    if row:
        road_type = row[0]
        return TRAFFIC_WEIGHTS.get(road_type, 0.1)

    return 0.1


def get_poi_counts_in_radius(lat, lon, radius=500):

    query = """
        SELECT category, COUNT(*) as count
        FROM poi_data
        WHERE ST_DWithin(
            location, 
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
            %s
        )
        GROUP BY category;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [lon, lat, radius])
        rows = cursor.fetchall()

    counts = {row[0]: row[1] for row in rows}

    return counts

def check_proximity_to_feedup(lat, lon, min_dist=600):
    query = """
        SELECT EXISTS (
            SELECT 1 FROM poi_data 
            WHERE category = 'feed_up' 
            AND ST_DWithin(location, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)
        );
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [lon, lat, min_dist])
        return cursor.fetchone()[0] # True or False



def calculate_location_score(lat, lon, potential_rent=None):

    poi_counts = get_poi_counts_in_radius(lat, lon, radius=500)
    traffic_multiplier = get_road_traffic_multiplier(lat, lon)
    is_too_close_to_self = check_proximity_to_feedup(lat, lon, min_dist=600)

    traffic_points = traffic_multiplier * 10

    education_points = min(poi_counts.get('university', 0) * 3 +
                           poi_counts.get('school', 0) * 1.5, 10)

    transit_points = 10 if poi_counts.get('metro_station', 0) > 0 else 0

    competition_penalty = poi_counts.get('fast_food', 0) * 1.5

    weights = {
        'traffic': 0.4,  # 40%
        'education': 0.25,  # 25%
        'transit': 0.25,  # 25%
        'competition': -0.1  # -10% (penalty)
    }

    base_score = (
                         (traffic_points * weights['traffic']) +
                         (education_points * weights['education']) +
                         (transit_points * weights['transit']) +
                         (competition_penalty * weights['competition'])
                 ) * 10  # scale to 0-100


    if is_too_close_to_self:
        base_score *= 0.6

    if potential_rent and potential_rent > 2500:
        base_score -= 10

    final_score = round(base_score, 2)

    return max(0, min(100, final_score))
