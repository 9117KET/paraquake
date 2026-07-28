from paraquake.risk.attenuation import effective_intensity


def test_intensity_equals_magnitude_at_zero_distance_and_depth():
    assert effective_intensity(7.0, 0.0, 0.0) == 7.0


def test_intensity_decreases_with_distance():
    near = effective_intensity(7.0, 10.0, 10.0)
    far = effective_intensity(7.0, 200.0, 10.0)
    assert near > far


def test_intensity_decreases_with_depth():
    shallow = effective_intensity(7.0, 50.0, 5.0)
    deep = effective_intensity(7.0, 50.0, 60.0)
    assert shallow > deep


def test_intensity_increases_with_magnitude():
    small = effective_intensity(5.5, 50.0, 10.0)
    large = effective_intensity(7.5, 50.0, 10.0)
    assert large > small


def test_negative_distance_or_depth_are_clamped_not_erroring():
    # Defensive: should not raise even if given a slightly negative float from
    # upstream floating-point noise.
    value = effective_intensity(7.0, -0.001, -0.001)
    assert value == effective_intensity(7.0, 0.0, 0.0)
