import math

from paraquake.geospatial.distance import haversine_km


def test_same_point_is_zero_distance():
    assert haversine_km(41.0082, 28.9784, 41.0082, 28.9784) == 0.0


def test_known_distance_london_to_paris():
    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) is ~344 km great-circle.
    d = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
    assert math.isclose(d, 344, rel_tol=0.03)


def test_known_distance_new_york_to_los_angeles():
    # NYC (40.7128, -74.0060) to LA (34.0522, -118.2437) is ~3936 km great-circle.
    d = haversine_km(40.7128, -74.0060, 34.0522, -118.2437)
    assert math.isclose(d, 3936, rel_tol=0.03)


def test_distance_is_symmetric():
    a = haversine_km(35.6762, 139.6503, 38.2682, 140.8694)
    b = haversine_km(38.2682, 140.8694, 35.6762, 139.6503)
    assert math.isclose(a, b, rel_tol=1e-9)


def test_antipodal_points_span_half_earth_circumference():
    d = haversine_km(0, 0, 0, 180)
    assert math.isclose(d, math.pi * 6371.0, rel_tol=1e-6)
