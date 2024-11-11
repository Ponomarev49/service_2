import math

from read import Coordinates

RADIUS_OF_EARTH = 6371
ERROR = 0.01 # погрешность координат в километрах


def calculate_distance(coords1: Coordinates, coords2: Coordinates):
    lat1, lon1 = math.radians(coords1.latitude), math.radians(coords1.longitude)
    lat2, lon2 = math.radians(coords2.latitude), math.radians(coords2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    haversine_formula = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    angular_distance = 2 * math.atan2(math.sqrt(haversine_formula), math.sqrt(1 - haversine_formula))
    distance = RADIUS_OF_EARTH * angular_distance

    if distance <= ERROR:
        return True
    else:
        return False
