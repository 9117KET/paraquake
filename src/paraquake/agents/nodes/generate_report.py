"""Agent node: turn the deterministic trigger-engine output into a plain-English
underwriting brief via a Groq-hosted Llama model (LangChain's ChatGroq).
"""

from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage

from paraquake.agents.prompts import SYSTEM_PROMPT, build_report_prompt
from paraquake.agents.state import AgentState

DEFAULT_GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_llm():
    """Lazily construct the ChatGroq client so importing this module (and
    running tests against it with a mocked LLM) never requires GROQ_API_KEY.
    """
    from langchain_groq import ChatGroq

    return ChatGroq(model=DEFAULT_GROQ_MODEL, temperature=0.2)


def generate_report(state: AgentState) -> AgentState:
    notable_events = state.get("notable_events", [])
    portfolio_summary = state.get("portfolio_summary", {})
    retry_notes = state.get("qa_notes")

    prompt = build_report_prompt(notable_events, portfolio_summary, retry_notes=retry_notes)
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])

    return {**state, "report_markdown": response.content}
