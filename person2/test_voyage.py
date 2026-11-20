import json, datetime as dt
import pandas as pd
import voyage
from geo import haversine_km

START = dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc)
G = pd.DataFrame({"seq": [0, 1], "lat_deg": [0.0, 0.0], "lon_deg": [0.0, 2.0]})

def make_snap(path, lat, lon, wave=0.5):
    times = [(dt.datetime(2026, 11, 17) + dt.timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(168)]
    snap = {"response": {"hourly": {"time": times, "wave_height": [wave] * 168,
            "ocean_current_velocity": [0.0] * 168, "ocean_current_direction": [0] * 168}}}
    (path / f"marine_{lat:.2f}_{lon:.2f}.json").write_text(json.dumps(snap))

def test_hours_without_current(tmp_path, monkeypatch):
    monkeypatch.setattr(voyage, "CACHE", tmp_path)
    make_snap(tmp_path, 0.0, 0.0); make_snap(tmp_path, 0.0, 2.0)
    r = voyage.evaluate_voyage(G, START, 16)
    assert abs(r["hours"] - haversine_km(0, 0, 0, 2) / 1.852 / 16) < 1e-6
    assert r["mean_wave_m"] == 0.5 and r["warnings"] == []

def test_missing_forecast_is_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(voyage, "CACHE", tmp_path)          # empty cache
    r = voyage.evaluate_voyage(G, START, 16)
    assert r["mean_wave_m"] is None and any("without wave data" in w for w in r["warnings"])

def test_outside_forecast_not_reused(tmp_path, monkeypatch):
    monkeypatch.setattr(voyage, "CACHE", tmp_path)
    make_snap(tmp_path, 0.0, 0.0); make_snap(tmp_path, 0.0, 2.0)
    late = dt.datetime(2026, 12, 30, tzinfo=dt.timezone.utc)   # long after the forecast ends
    r = voyage.evaluate_voyage(G, late, 16)
    assert r["mean_wave_m"] is None

def test_no_weather_mode_is_labelled():
    r = voyage.evaluate_voyage(G, START, 16, use_weather=False)
    assert r["mean_wave_m"] == 0.0 and any("no forecast" in w for w in r["warnings"])
