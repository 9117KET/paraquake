"""Discrete parametric payout tiering.

Real parametric (re)insurance products typically pay out in discrete bands tied
to how far the observed parameter (here, effective_intensity) clears the
policy's attachment point (trigger_magnitude) -- not a smooth, continuous curve.
"""

from __future__ import annotations

from paraquake.config import PAYOUT_TIERS


def payout_tier(excess_over_trigger: float) -> tuple[int, float]:
    """Return (tier, payout_fraction) for how far intensity cleared the trigger.

    tier 0 / fraction 0.0 means the event did not clear the site's trigger at all.
    PAYOUT_TIERS is assumed sorted ascending by min_excess.
    """
    if excess_over_trigger < PAYOUT_TIERS[0][0]:
        return 0, 0.0

    tier, fraction = 0, 0.0
    for i, (min_excess, frac) in enumerate(PAYOUT_TIERS, start=1):
        if excess_over_trigger >= min_excess:
            tier, fraction = i, frac
    return tier, fraction
