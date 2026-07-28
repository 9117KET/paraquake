"""Agent node: keep only the triggered results, ranked by payout, capped for
the report generator so it's never handed an unbounded prompt.
"""

from __future__ import annotations

from paraquake.agents.state import AgentState

MAX_NOTABLE_EVENTS = 10


def rank_and_filter(state: AgentState) -> AgentState:
    results = state.get("trigger_results", [])
    triggered = sorted((r for r in results if r.triggered), key=lambda r: r.payout_eur, reverse=True)
    return {**state, "notable_events": triggered[:MAX_NOTABLE_EVENTS]}
