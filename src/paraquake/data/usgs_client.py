"""Thin client for the USGS Earthquake Catalog (FDSNWS Event) API.

Free, public, no API key required:
https://earthquake.usgs.gov/fdsnws/event/1/
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

from paraquake.config import USGS_EVENT_API_URL
from paraquake.models import EarthquakeEvent

SAMPLE_FIXTURE_PATH = Path(__file__).resolve().parents[3] / "data" / "sample_usgs_response.json"


def _parse_geojson(payload: dict) -> list[EarthquakeEvent]:
    events: list[EarthquakeEvent] = []
    for feature in payload.get("features", []):
        props = feature["properties"]
        lon, lat, depth_km = feature["geometry"]["coordinates"]
        mag = props.get("mag")
        if mag is None:
            continue
        events.append(
            EarthquakeEvent(
                event_id=feature["id"],
                place=props.get("place") or "unknown location",
                magnitude=float(mag),
                latitude=float(lat),
                longitude=float(lon),
                depth_km=float(depth_km),
                time_ms=int(props["time"]),
            )
        )
    return events


def fetch_earthquakes(
    start_date: str,
    end_date: str,
    min_magnitude: float = 5.0,
    timeout: float = 15.0,
) -> list[EarthquakeEvent]:
    """Fetch real earthquake events from the USGS catalog for [start_date, end_date).

    Dates are 'YYYY-MM-DD' strings. Raises requests.RequestException on network
    failure -- callers (agent nodes) are expected to handle that explicitly
    rather than silently falling back, so a demo run never quietly shows stale data.
    """
    params = {
        "format": "geojson",
        "starttime": start_date,
        "endtime": end_date,
        "minmagnitude": min_magnitude,
    }
    response = requests.get(USGS_EVENT_API_URL, params=params, timeout=timeout)
    response.raise_for_status()
    return _parse_geojson(response.json())


def load_sample_fixture(min_magnitude: float = 0.0) -> list[EarthquakeEvent]:
    """Load the checked-in real USGS response fixture (offline, no network call)."""
    payload = json.loads(SAMPLE_FIXTURE_PATH.read_text(encoding="utf-8"))
    events = _parse_geojson(payload)
    return [e for e in events if e.magnitude >= min_magnitude]
