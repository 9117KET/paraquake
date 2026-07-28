"""Agent node: run the geospatial parametric trigger/payout engine over every
(event, site) candidate pair and summarize the portfolio-level result.
"""

from __future__ import annotations

from paraquake.agents.state import AgentState
from paraquake.risk.trigger import evaluate_portfolio


def compute_triggers(state: AgentState) -> AgentState:
    events = state.get("events", [])
    portfolio = state.get("portfolio", [])
    results = evaluate_portfolio(events, portfolio)

    triggered = [r for r in results if r.triggered]
    summary = {
        "total_sites": len(portfolio),
        "total_events_evaluated": len(events),
        "candidate_pairs": len(results),
        "triggered_pairs": len(triggered),
        "sites_triggered": len({r.site.site_id for r in triggered}),
        "total_payout_eur": sum(r.payout_eur for r in triggered),
        "largest_single_payout_eur": max((r.payout_eur for r in triggered), default=0.0),
    }
    return {**state, "trigger_results": results, "portfolio_summary": summary}
