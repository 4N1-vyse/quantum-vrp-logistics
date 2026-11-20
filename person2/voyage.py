"""Sail one passage with one vessel speed, using the cached forecast (Person 2)."""
import json, pathlib, datetime as dt
from geo import haversine_km, bearing_deg, segment_hours
from conditions import current_at

CACHE = pathlib.Path("cache")

def load_snap(lat, lon):
    p = CACHE / f"marine_{lat:.2f}_{lon:.2f}.json"
    return json.loads(p.read_text()) if p.exists() else None

def wave_at(snap, when):
    h = snap["response"]["hourly"]
    start = dt.datetime.fromisoformat(h["time"][0]).replace(tzinfo=dt.timezone.utc)
    i = round((when - start).total_seconds() / 3600)
    if i < 0 or i >= len(h["time"]):
        return None                      # outside forecast: never reuse the last value
    return h["wave_height"][i]

def evaluate_voyage(g, depart, speed_kn, use_weather=True):
    """g = rows of ONE passage. Returns hours, arrival, distance, wave stats, warnings."""
    g = g.sort_values("seq")
    pts = list(zip(g["lat_deg"], g["lon_deg"]))
    t, total_h, total_nmi = depart, 0.0, 0.0
    waves, no_wave, no_cur = [], 0, 0
    for (la1, lo1), (la2, lo2) in zip(pts[:-1], pts[1:]):
        dist = haversine_km(la1, lo1, la2, lo2) / 1.852
        hd = bearing_deg(la1, lo1, la2, lo2)
        cur, ws = None, []
        if use_weather:
            for s in (load_snap(la1, lo1), load_snap(la2, lo2)):
                if s is None:
                    continue
                if cur is None:
                    cur = current_at(s, t)
                w = wave_at(s, t)
                if w is not None:
                    ws.append(w)
            if cur is None:
                no_cur += 1
        cur = cur or (0.0, 0.0)          # no current data -> assume 0 and warn
        seg_h = segment_hours(dist, speed_kn, cur[0], cur[1], hd)
        if ws:
            waves.append((sum(ws) / len(ws), seg_h))
        elif use_weather:
            no_wave += 1
        t += dt.timedelta(hours=seg_h)
        total_h += seg_h
        total_nmi += dist
    warnings = []
    if not use_weather:
        warnings.append("no forecast used (waves and currents ignored)")
    if no_cur:
        warnings.append(f"{no_cur} segment(s) without current data (assumed 0)")
    if no_wave:
        warnings.append(f"{no_wave} segment(s) without wave data")
    if waves:
        mean_wave = sum(w * h for w, h in waves) / sum(h for _, h in waves)
        max_wave = max(w for w, _ in waves)
    else:
        mean_wave = None if use_weather else 0.0
        max_wave = mean_wave
    return {"hours": total_h, "arrival": t, "dist_nmi": total_nmi,
            "mean_wave_m": mean_wave, "max_wave_m": max_wave, "warnings": warnings}
