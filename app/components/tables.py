"""DataFrame builders for the Portfolio and Trigger Results tabs."""

from __future__ import annotations

import pandas as pd

from paraquake.models import ExposureSite, TriggerResult


def portfolio_dataframe(portfolio: list[ExposureSite], trigger_results: list[TriggerResult]) -> pd.DataFrame:
    by_site: dict[str, TriggerResult] = {}
    for r in trigger_results:
        current = by_site.get(r.site.site_id)
        if current is None or r.payout_eur > current.payout_eur:
            by_site[r.site.site_id] = r

    rows = []
    for site in portfolio:
        result = by_site.get(site.site_id)
        rows.append(
            {
                "Site": site.site_name,
                "Region": site.region,
                "Type": site.exposure_type,
                "Construction": site.construction_class,
                "Sum Insured (EUR)": site.sum_insured_eur,
                "Trigger Mw": site.trigger_magnitude,
                "Radius (km)": site.trigger_radius_km,
                "Status": "Triggered" if result and result.triggered else ("Evaluated" if result else "No candidate event"),
                "Tier": result.tier if result else 0,
                "Payout (EUR)": result.payout_eur if result else 0.0,
            }
        )
    return pd.DataFrame(rows)


def trigger_results_dataframe(trigger_results: list[TriggerResult]) -> pd.DataFrame:
    triggered = sorted((r for r in trigger_results if r.triggered), key=lambda r: r.payout_eur, reverse=True)
    rows = [
        {
            "Site": r.site.site_name,
            "Region": r.site.region,
            "Event": r.event.place,
            "Event Date": r.event.iso_time,
            "Magnitude": r.event.magnitude,
            "Distance (km)": round(r.distance_km, 1),
            "Effective Intensity": round(r.effective_intensity, 2),
            "Tier": r.tier,
            "Payout (EUR)": r.payout_eur,
        }
        for r in triggered
    ]
    return pd.DataFrame(rows)
