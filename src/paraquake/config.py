"""Tunable constants for the geospatial/risk engine.

All coefficients below are illustrative and chosen to produce a plausible,
directionally-correct demo -- they are NOT calibrated against real ground-motion
prediction equations (GMPEs) or empirical loss data. See README.md ("Limitations")
before drawing any real-world conclusions from this project's output.
"""

USGS_EVENT_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# An event is only considered for a site if it lands within the site's own
# trigger radius (the "cat-in-a-circle" parametric design) and is shallow
# enough to plausibly cause strong surface shaking.
MAX_TRIGGER_DEPTH_KM = 70.0

# effective_intensity = magnitude - ATTEN_DIST_COEF * log10(distance_km + 1) - ATTEN_DEPTH_COEF * depth_km
# Loosely mirrors the shape of real attenuation (intensity decays with log-distance
# and with depth) but is NOT a fitted/validated GMPE.
ATTEN_DIST_COEF = 1.5
ATTEN_DEPTH_COEF = 0.001

# Discrete parametric payout tiers, keyed by how far effective_intensity clears
# the site's own trigger_magnitude attachment point.
PAYOUT_TIERS = (
    # (min_excess_over_trigger, payout_fraction_of_max_payout)
    (0.0, 0.25),
    (1.0, 0.60),
    (2.0, 1.00),
)

EARTH_RADIUS_KM = 6371.0

DEFAULT_MIN_MAGNITUDE = 5.0

# Regex the QA guardrail node uses to confirm the LLM report carries the
# mandatory limitations disclaimer before it's shown to a user.
DISCLAIMER_PATTERN = r"(educational|demo|not\s+an?\s+actuarial|illustrative|simplified)"
