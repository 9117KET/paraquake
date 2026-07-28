"""Core data structures shared across the ingestion, risk, and agent layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EarthquakeEvent:
    event_id: str
    place: str
    magnitude: float
    latitude: float
    longitude: float
    depth_km: float
    time_ms: int  # epoch milliseconds, as returned by USGS

    @property
    def iso_time(self) -> str:
        from datetime import datetime, timezone

        return datetime.fromtimestamp(self.time_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


@dataclass(frozen=True)
class ExposureSite:
    site_id: str
    site_name: str
    country: str
    region: str
    latitude: float
    longitude: float
    exposure_type: str
    construction_class: str
    sum_insured_eur: float
    trigger_magnitude: float
    trigger_radius_km: float
    max_payout_eur: float
    currency: str = "EUR"


@dataclass(frozen=True)
class TriggerResult:
    event: EarthquakeEvent
    site: ExposureSite
    distance_km: float
    effective_intensity: float
    tier: int
    payout_fraction: float
    payout_eur: float

    @property
    def triggered(self) -> bool:
        return self.tier > 0
