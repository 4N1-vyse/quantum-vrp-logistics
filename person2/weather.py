"""Fetch and cache real marine forecasts from Open-Meteo (Person 2)."""
import json, pathlib, datetime as dt
import requests

URL = "https://marine-api.open-meteo.com/v1/marine"
HOURLY = "wave_height,ocean_current_velocity,ocean_current_direction"
CACHE = pathlib.Path("cache")
CACHE.mkdir(exist_ok=True)

def fetch_marine(lat, lon, days=7):
    path = CACHE / f"marine_{lat:.2f}_{lon:.2f}.json"
    if path.exists():                      # reuse saved answer (caching)
        return json.loads(path.read_text())
    params = {"latitude": lat, "longitude": lon, "hourly": HOURLY,
              "forecast_days": days, "timezone": "GMT"}
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    snap = {"fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": "Open-Meteo Marine API", "url": r.url, "response": r.json()}
    path.write_text(json.dumps(snap, indent=1))
    return snap

if __name__ == "__main__":
    snap = fetch_marine(19.5, 68.0)
    h = snap["response"]["hourly"]
    print("units:", snap["response"]["hourly_units"])
    print("first times:", h["time"][:3])
    print("wave_height:", h["wave_height"][:3])
    print("current speed:", h["ocean_current_velocity"][:3])
    print("current direction:", h["ocean_current_direction"][:3])
