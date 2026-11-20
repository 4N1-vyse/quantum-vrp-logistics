import math
from datetime import datetime, timedelta

def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great-circle distance between two coordinates.

    Returns distance in kilometres.
    """

    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_km * c


def calculate_passage_distance_km(waypoints) -> float:
    """
    Calculate total passage distance from an ordered list
    of waypoint objects.
    """

    if len(waypoints) < 2:
        return 0.0

    total_distance = 0.0

    for i in range(len(waypoints) - 1):
        current = waypoints[i]
        next_waypoint = waypoints[i + 1]

        distance = calculate_distance_km(
            current.lat_deg,
            current.lon_deg,
            next_waypoint.lat_deg,
            next_waypoint.lon_deg
        )

        total_distance += distance

    return total_distance


def calculate_travel_hours(
    distance_km: float,
    speed_kn: float
) -> float:
    """
    Calculate estimated travel time in hours.

    Vessel speed is provided in knots.
    """

    if distance_km < 0:
        raise ValueError("Distance cannot be negative")

    if speed_kn <= 0:
        raise ValueError("Vessel speed must be greater than zero")

    speed_kmh = speed_kn * 1.852

    return distance_km / speed_kmh


def calculate_estimated_arrival_utc(
    departure_utc: datetime,
    travel_hours: float
) -> datetime:
    """
    Calculate estimated arrival time in UTC.
    """

    if departure_utc.tzinfo is None:
        raise ValueError("Departure time must be timezone-aware")

    if travel_hours < 0:
        raise ValueError("Travel time cannot be negative")

    return departure_utc + timedelta(hours=travel_hours)
