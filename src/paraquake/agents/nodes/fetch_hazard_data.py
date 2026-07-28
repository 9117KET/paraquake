"""Agent node: fetch real earthquake events from USGS (or an offline fixture)."""

from __future__ import annotations

from paraquake.agents.state import AgentState
from paraquake.data.usgs_client import fetch_earthquakes, load_sample_fixture


def fetch_hazard_data(state: AgentState) -> AgentState:
    if state.get("use_offline_fixture"):
        events = load_sample_fixture(min_magnitude=state.get("min_magnitude", 5.0))
    else:
        events = fetch_earthquakes(
            start_date=state["start_date"],
            end_date=state["end_date"],
            min_magnitude=state.get("min_magnitude", 5.0),
        )
    return {**state, "events": events}
