"""Builds the pydeck map: exposure sites, earthquake epicenters, and arcs
connecting sites to the events that triggered a payout for them.
"""

from __future__ import annotations

import pydeck as pdk

from paraquake.models import EarthquakeEvent, ExposureSite, TriggerResult

TIER_COLORS = {
    0: [148, 163, 184],  # slate grey -- not triggered / no data yet
    1: [241, 196, 15],  # yellow
    2: [230, 126, 34],  # orange
    3: [192, 57, 43],  # red
}


def _site_max_tier(site: ExposureSite, trigger_results: list[TriggerResult]) -> int:
    tiers = [r.tier for r in trigger_results if r.site.site_id == site.site_id]
    return max(tiers, default=0)


def build_site_rows(portfolio: list[ExposureSite], trigger_results: list[TriggerResult]) -> list[dict]:
    rows = []
    for site in portfolio:
        tier = _site_max_tier(site, trigger_results)
        rows.append(
            {
                "site_name": site.site_name,
                "region": site.region,
                "lat": site.latitude,
                "lon": site.longitude,
                "sum_insured_eur": site.sum_insured_eur,
                "tier": tier,
                "radius": 15000 + site.sum_insured_eur / 4000,
                "color": TIER_COLORS[tier],
            }
        )
    return rows


def build_event_rows(events: list[EarthquakeEvent]) -> list[dict]:
    return [
        {
            "place": e.place,
            "lat": e.latitude,
            "lon": e.longitude,
            "magnitude": e.magnitude,
            "radius": max(e.magnitude, 1) * 15000,
        }
        for e in events
    ]


def build_arc_rows(trigger_results: list[TriggerResult]) -> list[dict]:
    return [
        {
            "from_lon": r.event.longitude,
            "from_lat": r.event.latitude,
            "to_lon": r.site.longitude,
            "to_lat": r.site.latitude,
            "color": TIER_COLORS[r.tier],
            "tooltip": f"{r.event.place} -> {r.site.site_name}: EUR {r.payout_eur:,.0f}",
        }
        for r in trigger_results
        if r.triggered
    ]


def build_deck(
    portfolio: list[ExposureSite],
    events: list[EarthquakeEvent],
    trigger_results: list[TriggerResult],
) -> pdk.Deck:
    site_rows = build_site_rows(portfolio, trigger_results)
    event_rows = build_event_rows(events)
    arc_rows = build_arc_rows(trigger_results)

    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=site_rows,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
            opacity=0.75,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=event_rows,
            get_position="[lon, lat]",
            get_fill_color=[30, 60, 200, 140],
            get_radius="radius",
            pickable=True,
            opacity=0.5,
        ),
    ]

    if arc_rows:
        layers.append(
            pdk.Layer(
                "ArcLayer",
                data=arc_rows,
                get_source_position="[from_lon, from_lat]",
                get_target_position="[to_lon, to_lat]",
                get_source_color="color",
                get_target_color="color",
                get_width=2,
                pickable=True,
            )
        )

    view_state = pdk.ViewState(latitude=15, longitude=40, zoom=1.1, pitch=0)

    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style=None,
        tooltip={"text": "{site_name}{place}"},
    )
