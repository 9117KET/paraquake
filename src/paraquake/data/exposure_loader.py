"""Loads the synthetic exposure portfolio (data/exposure_portfolio.csv).

The portfolio itself is entirely synthetic and illustrative -- no real insurer's
policyholder data is used or implied. Only the hazard data (earthquake events,
via usgs_client) is real.
"""

from __future__ import annotations

import csv
from pathlib import Path

from paraquake.models import ExposureSite

DEFAULT_PORTFOLIO_PATH = Path(__file__).resolve().parents[3] / "data" / "exposure_portfolio.csv"


def load_exposure_portfolio(path: Path | str = DEFAULT_PORTFOLIO_PATH) -> list[ExposureSite]:
    path = Path(path)
    sites: list[ExposureSite] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sites.append(
                ExposureSite(
                    site_id=row["site_id"],
                    site_name=row["site_name"],
                    country=row["country"],
                    region=row["region"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    exposure_type=row["exposure_type"],
                    construction_class=row["construction_class"],
                    sum_insured_eur=float(row["sum_insured_eur"]),
                    trigger_magnitude=float(row["trigger_magnitude"]),
                    trigger_radius_km=float(row["trigger_radius_km"]),
                    max_payout_eur=float(row["max_payout_eur"]),
                    currency=row.get("currency", "EUR"),
                )
            )
    return sites
