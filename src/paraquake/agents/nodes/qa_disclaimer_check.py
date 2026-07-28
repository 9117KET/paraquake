"""Agent node: a factuality/compliance guardrail on the LLM-generated report.

Checks (1) the mandatory Limitations disclaimer sentence is present, and
(2) every EUR figure the report mentions matches a real, known ground-truth
number from the deterministic risk engine (never something the model invented).
This directly mirrors the reliability discipline from the RAG-hallucination
work this project's author studied: don't trust generated text with numbers
in it until you've checked it against ground truth.
"""

from __future__ import annotations

import re

from paraquake.agents.state import AgentState
from paraquake.config import DISCLAIMER_PATTERN
from paraquake.models import TriggerResult

MAX_RETRIES = 1
MONEY_PATTERN = re.compile(r"€\s?([\d][\d,]*(?:\.\d+)?)|([\d][\d,]*(?:\.\d+)?)\s?EUR", re.IGNORECASE)
MATCH_TOLERANCE = 0.02


def _extract_money_figures(text: str) -> list[float]:
    values = []
    for m in MONEY_PATTERN.finditer(text):
        raw = m.group(1) or m.group(2)
        try:
            values.append(float(raw.replace(",", "")))
        except ValueError:
            continue
    return values


def _ground_truth_values(portfolio_summary: dict, notable_events: list[TriggerResult]) -> set[float]:
    values = {
        float(portfolio_summary.get("total_payout_eur", 0.0)),
        float(portfolio_summary.get("largest_single_payout_eur", 0.0)),
    }
    for r in notable_events:
        values.add(r.payout_eur)
        values.add(r.site.sum_insured_eur)
        values.add(r.site.max_payout_eur)
    return values


def _figures_not_grounded(mentioned: list[float], ground_truth: set[float]) -> list[str]:
    problems = []
    nonzero_truths = [g for g in ground_truth if g]
    for value in mentioned:
        if value == 0:
            continue
        if not any(abs(value - g) / g <= MATCH_TOLERANCE for g in nonzero_truths):
            problems.append(
                f"The figure {value:,.0f} EUR does not match any computed portfolio figure; "
                "only use numbers from the data provided."
            )
    return problems


def qa_disclaimer_check(state: AgentState) -> AgentState:
    report = state.get("report_markdown", "")
    notable_events = state.get("notable_events", [])
    summary = state.get("portfolio_summary", {})
    retry_count = state.get("qa_retry_count", 0)

    notes: list[str] = []
    if not re.search(DISCLAIMER_PATTERN, report, re.IGNORECASE):
        notes.append(
            "Missing the mandatory Limitations disclaimer sentence "
            "(must state this is a simplified, educational, non-actuarial demo)."
        )

    mentioned = _extract_money_figures(report)
    ground_truth = _ground_truth_values(summary, notable_events)
    notes.extend(_figures_not_grounded(mentioned, ground_truth))

    passed = len(notes) == 0
    return {
        **state,
        "qa_passed": passed,
        "qa_notes": notes,
        "qa_retry_count": retry_count if passed else retry_count + 1,
    }


def route_after_qa(state: AgentState) -> str:
    if state.get("qa_passed"):
        return "end"
    if state.get("qa_retry_count", 0) <= MAX_RETRIES:
        return "retry"
    return "end"
