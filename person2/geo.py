import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def bearing_deg(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def passage_nmi(df):
    df = df.sort_values("seq")
    pts = list(zip(df["lat_deg"], df["lon_deg"]))
    km = sum(haversine_km(*a, *b) for a, b in zip(pts[:-1], pts[1:]))
    return km / 1.852

def segment_hours(dist_nmi, ship_kn, current_kn, current_to_deg, heading_deg):
    along = current_kn * math.cos(math.radians(current_to_deg - heading_deg))
    return dist_nmi / (ship_kn + along)
