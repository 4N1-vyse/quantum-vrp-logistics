import datetime as dt
from conditions import current_at
from geo import segment_hours

SNAP = {"response": {"hourly": {
    "time": ["2026-11-12T00:00", "2026-11-12T01:00", "2026-11-12T02:00"],
    "ocean_current_velocity": [0.8, 1.852, None],
    "ocean_current_direction": [207, 90, 90]}}}

def utc(h):
    return dt.datetime(2026, 11, 12, h, tzinfo=dt.timezone.utc)

def test_units_converted_to_knots():
    kn, d = current_at(SNAP, utc(1))
    assert abs(kn - 1.0) < 1e-6 and d == 90

def test_outside_horizon_returns_none():
    assert current_at(SNAP, dt.datetime(2026, 11, 20, tzinfo=dt.timezone.utc)) is None

def test_missing_value_returns_none():
    assert current_at(SNAP, utc(2)) is None

def test_real_segment_example():
    assert abs(segment_hours(381.4, 16, 0.432, 207, 299.2) - 23.865) < 0.01
