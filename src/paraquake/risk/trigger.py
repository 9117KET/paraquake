"""Ties distance, attenuation, and payout tiering into a single per-(event, site)
parametric trigger evaluation -- the "cat-in-a-circle" design used by real
parametric earthquake covers (e.g. CCRIF SPC, IBRD/FONDEN cat bonds).
"""

from __future__ import annotations

from paraquake.config import MAX_TRIGGER_DEPTH_KM
from paraquake.geospatial.distance import haversine_km
from paraquake.models import EarthquakeEvent, ExposureSite, TriggerResult
from paraquake.risk.attenuation import effective_intensity
from paraquake.risk.payout import payout_tier


def evaluate_trigger(event: EarthquakeEvent, site: ExposureSite) -> TriggerResult | None:
    """Evaluate whether `event` is even a candidate for `site`'s parametric cover,
    and if so, compute its trigger tier and payout.

    Returns None if the event falls outside the site's trigger radius or is too
    deep to plausibly cause strong surface shaking -- these events are not
    "candidates" and are excluded before any intensity/payout math runs.
    """
    distance_km = haversine_km(event.latitude, event.longitude, site.latitude, site.longitude)

    if distance_km > site.trigger_radius_km or event.depth_km > MAX_TRIGGER_DEPTH_KM:
        return None

    intensity = effective_intensity(event.magnitude, distance_km, event.depth_km)
    excess = intensity - site.trigger_magnitude
    tier, fraction = payout_tier(excess)
    payout_eur = fraction * site.max_payout_eur

    return TriggerResult(
        event=event,
        site=site,
        distance_km=distance_km,
        effective_intensity=intensity,
        tier=tier,
        payout_fraction=fraction,
        payout_eur=payout_eur,
    )


def evaluate_portfolio(
    events: list[EarthquakeEvent], sites: list[ExposureSite]
) -> list[TriggerResult]:
    """Evaluate every (event, site) candidate pair; only candidates are returned
    (i.e. results where the event fell inside the site's trigger radius and
    depth cutoff), regardless of whether they actually triggered a payout.
    """
    results: list[TriggerResult] = []
    for event in events:
        for site in sites:
            result = evaluate_trigger(event, site)
            if result is not None:
                results.append(result)
    return results
