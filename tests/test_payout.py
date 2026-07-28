from paraquake.risk.payout import payout_tier


def test_below_trigger_pays_nothing():
    tier, fraction = payout_tier(-0.5)
    assert tier == 0
    assert fraction == 0.0


def test_exactly_at_trigger_pays_tier_one():
    tier, fraction = payout_tier(0.0)
    assert tier == 1
    assert fraction == 0.25


def test_mid_tier_two():
    tier, fraction = payout_tier(1.5)
    assert tier == 2
    assert fraction == 0.60


def test_top_tier_at_and_above_two():
    tier, fraction = payout_tier(2.0)
    assert tier == 3
    assert fraction == 1.00

    tier, fraction = payout_tier(5.0)
    assert tier == 3
    assert fraction == 1.00


def test_tier_is_monotonic_non_decreasing_in_excess():
    fractions = [payout_tier(x)[1] for x in [-1, -0.01, 0, 0.5, 0.99, 1.0, 1.99, 2.0, 3.0]]
    assert fractions == sorted(fractions)
