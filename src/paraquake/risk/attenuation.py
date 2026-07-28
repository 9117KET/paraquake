"""A deliberately simplified ground-shaking attenuation model.

This is NOT a calibrated ground-motion prediction equation (GMPE). It exists to
give the demo a directionally-correct, testable relationship where intensity:
  - increases with earthquake magnitude,
  - decreases with distance from the epicenter (log-distance decay), and
  - decreases (slightly) with hypocentral depth.

A production NatCat model would replace this with a peer-reviewed GMPE plus
local soil/site amplification factors. See README.md ("Limitations").
"""

from __future__ import annotations

import math

from paraquake.config import ATTEN_DEPTH_COEF, ATTEN_DIST_COEF


def effective_intensity(magnitude: float, distance_km: float, depth_km: float) -> float:
    """Return a simplified, unitless 'effective intensity' at a site.

    distance_km and depth_km are clamped to be non-negative; distance is floored
    at 0 before the +1 offset so log10 is always well-defined (avoids log(0) at
    the epicenter itself).
    """
    distance_km = max(distance_km, 0.0)
    depth_km = max(depth_km, 0.0)
    return magnitude - ATTEN_DIST_COEF * math.log10(distance_km + 1) - ATTEN_DEPTH_COEF * depth_km
