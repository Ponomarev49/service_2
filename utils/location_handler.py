import math
from .constants import RADIUS_OF_EARTH

class Coordinates:
    def __init__(self, coordinates_list):
        self.latitude = float(coordinates_list[0])
        self.longitude = float(coordinates_list[1])


def calculate_distance(coords1: Coordinates, coords2: Coordinates):
    lat1, lon1 = math.radians(coords1.latitude), math.radians(coords1.longitude)
    lat2, lon2 = math.radians(coords2.latitude), math.radians(coords2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    haversine_formula = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    angular_distance = 2 * math.atan2(math.sqrt(haversine_formula), math.sqrt(1 - haversine_formula))
    distance = RADIUS_OF_EARTH * angular_distance

    return distance
