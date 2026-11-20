from geo import haversine_km, segment_hours, bearing_deg

def test_same_point():
    assert haversine_km(10, 20, 10, 20) == 0

def test_two_degrees():
    assert abs(haversine_km(0, 0, 0, 2) - 222.4) < 0.5

def test_bearing_east():
    assert abs(bearing_deg(0, 0, 0, 1) - 90) < 0.01

def test_current():
    assert abs(segment_hours(100, 16, 0.8, 90, 300) - 6.53) < 0.01
