import math

from read import Coordinates


def calculate_distance(coords1 : Coordinates, coords2 : Coordinates):
    lat1, lon1 = math.radians(coords1.latitude), math.radians(coords1.longitude)
    lat2, lon2 = math.radians(coords2.latitude), math.radians(coords2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius_of_earth = 6371
    distance = radius_of_earth * c

    if distance <= 0.01:
        answer = 'Вы на работе'
    else:
        answer = 'Вы не на работе'
    return answer
