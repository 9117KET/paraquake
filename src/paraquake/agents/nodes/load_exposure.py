"""Agent node: load the synthetic exposure portfolio."""

from __future__ import annotations

from paraquake.agents.state import AgentState
from paraquake.data.exposure_loader import load_exposure_portfolio


def load_exposure(state: AgentState) -> AgentState:
    portfolio = load_exposure_portfolio()
    return {**state, "portfolio": portfolio}
