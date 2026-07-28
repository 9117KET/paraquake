from paraquake.data.usgs_client import load_sample_fixture


def test_load_sample_fixture_returns_events():
    events = load_sample_fixture()
    assert len(events) > 0


def test_sample_fixture_contains_the_turkey_syria_m78_event():
    # 2023-02-06 Turkey-Syria earthquake, USGS event id us6000jllz, M7.8.
    events = load_sample_fixture()
    ids = {e.event_id for e in events}
    assert "us6000jllz" in ids
    turkey_event = next(e for e in events if e.event_id == "us6000jllz")
    assert turkey_event.magnitude >= 7.5
    assert turkey_event.depth_km < 20  # shallow, consistent with the real event record


def test_min_magnitude_filter():
    all_events = load_sample_fixture(min_magnitude=0.0)
    filtered = load_sample_fixture(min_magnitude=6.0)
    assert len(filtered) <= len(all_events)
    assert all(e.magnitude >= 6.0 for e in filtered)


def test_event_fields_are_well_typed():
    events = load_sample_fixture()
    sample = events[0]
    assert isinstance(sample.magnitude, float)
    assert isinstance(sample.latitude, float)
    assert isinstance(sample.longitude, float)
    assert isinstance(sample.depth_km, float)
    assert isinstance(sample.time_ms, int)
    assert len(sample.iso_time) == 10  # YYYY-MM-DD
