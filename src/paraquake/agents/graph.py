"""Builds and runs the ParaQuake LangGraph pipeline:

fetch_hazard_data -> load_exposure -> compute_triggers -> rank_and_filter
    -> generate_report -> qa_disclaimer_check -(retry once on failure)-> generate_report
                                              -(pass, or retries exhausted)-> END
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from paraquake.agents.nodes.compute_triggers import compute_triggers
from paraquake.agents.nodes.fetch_hazard_data import fetch_hazard_data
from paraquake.agents.nodes.generate_report import generate_report
from paraquake.agents.nodes.load_exposure import load_exposure
from paraquake.agents.nodes.qa_disclaimer_check import qa_disclaimer_check, route_after_qa
from paraquake.agents.nodes.rank_and_filter import rank_and_filter
from paraquake.agents.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("fetch_hazard_data", fetch_hazard_data)
    graph.add_node("load_exposure", load_exposure)
    graph.add_node("compute_triggers", compute_triggers)
    graph.add_node("rank_and_filter", rank_and_filter)
    graph.add_node("generate_report", generate_report)
    graph.add_node("qa_disclaimer_check", qa_disclaimer_check)

    graph.set_entry_point("fetch_hazard_data")
    graph.add_edge("fetch_hazard_data", "load_exposure")
    graph.add_edge("load_exposure", "compute_triggers")
    graph.add_edge("compute_triggers", "rank_and_filter")
    graph.add_edge("rank_and_filter", "generate_report")
    graph.add_edge("generate_report", "qa_disclaimer_check")
    graph.add_conditional_edges(
        "qa_disclaimer_check",
        route_after_qa,
        {"retry": "generate_report", "end": END},
    )

    return graph.compile()


def run_pipeline(
    start_date: str,
    end_date: str,
    min_magnitude: float = 5.0,
    use_offline_fixture: bool = False,
) -> AgentState:
    app = build_graph()
    initial_state: AgentState = {
        "start_date": start_date,
        "end_date": end_date,
        "min_magnitude": min_magnitude,
        "use_offline_fixture": use_offline_fixture,
        "qa_retry_count": 0,
    }
    return app.invoke(initial_state)
