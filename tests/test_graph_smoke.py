"""End-to-end LangGraph smoke tests with a mocked LLM (no network, no API key)."""

from __future__ import annotations

import paraquake.agents.nodes.generate_report as generate_report_module
from paraquake.agents.graph import build_graph


class _FakeMessage:
    def __init__(self, content: str):
        self.content = content


class _FakeLLM:
    def __init__(self, responses: list[str]):
        self._responses = responses
        self.calls = 0

    def invoke(self, _messages):
        content = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return _FakeMessage(content)


GOOD_REPORT = (
    "## Portfolio Brief\n\nSeveral sites were evaluated this run.\n\n"
    "Limitations: this is a simplified, educational demo and not an actuarial-grade "
    "catastrophe model; the exposure portfolio is synthetic."
)

BAD_REPORT_NO_DISCLAIMER = "## Portfolio Brief\n\nEverything looks fine, no caveats needed."


def _base_state():
    return {
        "start_date": "2023-02-06",
        "end_date": "2023-02-07",
        "min_magnitude": 5.0,
        "use_offline_fixture": True,
        "qa_retry_count": 0,
    }


def test_pipeline_runs_end_to_end_and_passes_qa(monkeypatch):
    monkeypatch.setattr(generate_report_module, "get_llm", lambda: _FakeLLM([GOOD_REPORT]))

    app = build_graph()
    final_state = app.invoke(_base_state())

    assert "events" in final_state and len(final_state["events"]) > 0
    assert "portfolio" in final_state and len(final_state["portfolio"]) == 20
    assert "trigger_results" in final_state
    assert final_state["qa_passed"] is True
    assert "Limitations" in final_state["report_markdown"]


def test_pipeline_retries_once_when_disclaimer_missing_then_passes(monkeypatch):
    fake = _FakeLLM([BAD_REPORT_NO_DISCLAIMER, GOOD_REPORT])
    monkeypatch.setattr(generate_report_module, "get_llm", lambda: fake)

    app = build_graph()
    final_state = app.invoke(_base_state())

    assert fake.calls == 2
    assert final_state["qa_passed"] is True
    assert final_state["report_markdown"] == GOOD_REPORT


def test_pipeline_gives_up_after_max_retries_and_flags_failure(monkeypatch):
    fake = _FakeLLM([BAD_REPORT_NO_DISCLAIMER])  # always bad
    monkeypatch.setattr(generate_report_module, "get_llm", lambda: fake)

    app = build_graph()
    final_state = app.invoke(_base_state())

    assert fake.calls == 2  # original attempt + one retry
    assert final_state["qa_passed"] is False
    assert final_state["qa_notes"]
