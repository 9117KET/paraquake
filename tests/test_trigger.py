from paraquake.models import EarthquakeEvent, ExposureSite
from paraquake.risk.trigger import evaluate_portfolio, evaluate_trigger

TOKYO_SITE = ExposureSite(
    site_id="SITE-TEST",
    site_name="Test Tokyo Site",
    country="Japan",
    region="Kanto",
    latitude=35.6762,
    longitude=139.6503,
    exposure_type="Commercial Property",
    construction_class="A",
    sum_insured_eur=10_000_000,
    trigger_magnitude=6.5,
    trigger_radius_km=100,
    max_payout_eur=2_000_000,
)


def _event(magnitude, lat, lon, depth_km=10.0, event_id="test-event"):
    return EarthquakeEvent(
        event_id=event_id,
        place="test",
        magnitude=magnitude,
        latitude=lat,
        longitude=lon,
        depth_km=depth_km,
        time_ms=0,
    )


def test_event_at_epicenter_above_trigger_pays_out():
    # magnitude 9.0 at zero distance gives effective_intensity ~8.99, well over
    # (trigger_magnitude 6.5 + 2.0) = 8.5, so this should land in the top tier.
    event = _event(magnitude=9.0, lat=35.6762, lon=139.6503)
    result = evaluate_trigger(event, TOKYO_SITE)
    assert result is not None
    assert result.triggered
    assert result.tier == 3
    assert result.payout_eur == TOKYO_SITE.max_payout_eur


def test_event_far_outside_radius_is_not_a_candidate():
    # roughly 9000km+ away
    event = _event(magnitude=9.0, lat=-33.4489, lon=-70.6693)
    result = evaluate_trigger(event, TOKYO_SITE)
    assert result is None


def test_event_too_deep_is_not_a_candidate():
    event = _event(magnitude=8.0, lat=35.6762, lon=139.6503, depth_km=500.0)
    result = evaluate_trigger(event, TOKYO_SITE)
    assert result is None


def test_event_within_radius_but_below_trigger_does_not_pay():
    event = _event(magnitude=4.0, lat=35.7, lon=139.7)
    result = evaluate_trigger(event, TOKYO_SITE)
    assert result is not None
    assert not result.triggered
    assert result.payout_eur == 0.0


def test_evaluate_portfolio_only_returns_candidates():
    events = [
        _event(magnitude=8.0, lat=35.6762, lon=139.6503, event_id="near-tokyo"),
        _event(magnitude=9.0, lat=-33.4489, lon=-70.6693, event_id="far-away"),
    ]
    results = evaluate_portfolio(events, [TOKYO_SITE])
    assert len(results) == 1
    assert results[0].event.event_id == "near-tokyo"
