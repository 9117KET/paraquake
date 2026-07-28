"""Shared state threaded through every node of the ParaQuake LangGraph pipeline."""

from __future__ import annotations

from typing import TypedDict

from paraquake.models import EarthquakeEvent, ExposureSite, TriggerResult


class AgentState(TypedDict, total=False):
    # inputs
    start_date: str
    end_date: str
    min_magnitude: float
    use_offline_fixture: bool

    # fetch_hazard_data
    events: list[EarthquakeEvent]

    # load_exposure
    portfolio: list[ExposureSite]

    # compute_triggers
    trigger_results: list[TriggerResult]
    portfolio_summary: dict

    # rank_and_filter
    notable_events: list[TriggerResult]

    # generate_report / qa_disclaimer_check
    report_markdown: str
    qa_passed: bool
    qa_retry_count: int
    qa_notes: list[str]
