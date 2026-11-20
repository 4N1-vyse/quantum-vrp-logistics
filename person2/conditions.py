import datetime as dt

KMH_TO_KN = 1 / 1.852

def current_at(snap, when_utc):
    """Return (speed_kn, direction_to_deg) at the hour nearest when_utc.
    Returns None if the time is outside the forecast or the value is missing."""
    h = snap["response"]["hourly"]
    start = dt.datetime.fromisoformat(h["time"][0]).replace(tzinfo=dt.timezone.utc)
    i = round((when_utc - start).total_seconds() / 3600)
    if i < 0 or i >= len(h["time"]):
        return None                      # outside forecast horizon: do NOT reuse last value
    v = h["ocean_current_velocity"][i]
    d = h["ocean_current_direction"][i]
    if v is None or d is None:
        return None
    return v * KMH_TO_KN, d
