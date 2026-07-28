"""Prompt construction for the generate_report agent node.

The LLM is only ever handed condensed markdown summaries of numbers already
computed by the deterministic risk engine -- never asked to compute or invent
figures itself. This keeps the QA guardrail's job simple: check that whatever
numbers the model *does* mention match the ground truth it was given.
"""

from __future__ import annotations

from paraquake.models import TriggerResult

SYSTEM_PROMPT = """You are an underwriting analyst assistant at a reinsurance company.
You write short, plain-English risk briefs for a parametric earthquake NatCat
portfolio, for an audience that includes both technical underwriters and
non-technical stakeholders (e.g. claims, finance).

Rules you must follow:
1. Only reference figures that appear in the data given to you below. Never
   estimate, round loosely, or invent a number that isn't present.
2. Keep it concise: a short headline, 3-6 sentences of narrative, then a
   bullet list of the top triggered sites.
3. You MUST end with a "Limitations" sentence stating this is a simplified,
   educational demo, not an actuarial-grade catastrophe model, and that the
   exposure portfolio is synthetic.
4. Do not use em dashes.
"""


def _format_notable_events(notable_events: list[TriggerResult]) -> str:
    if not notable_events:
        return "No sites were triggered in this run."
    lines = ["| Site | Region | Event | Magnitude | Distance (km) | Tier | Payout (EUR) |",
              "|---|---|---|---|---|---|---|"]
    for r in notable_events:
        lines.append(
            f"| {r.site.site_name} | {r.site.region} | {r.event.place} | "
            f"{r.event.magnitude:.1f} | {r.distance_km:.0f} | {r.tier} | {r.payout_eur:,.0f} |"
        )
    return "\n".join(lines)


def build_report_prompt(
    notable_events: list[TriggerResult],
    portfolio_summary: dict,
    retry_notes: list[str] | None = None,
) -> str:
    table = _format_notable_events(notable_events)
    summary_lines = "\n".join(f"- {k}: {v}" for k, v in portfolio_summary.items())

    correction = ""
    if retry_notes:
        correction = (
            "\n\nIMPORTANT CORRECTION from a QA check on your previous draft, fix these issues:\n"
            + "\n".join(f"- {note}" for note in retry_notes)
        )

    return f"""Portfolio summary:
{summary_lines}

Top triggered sites this run:
{table}
{correction}

Write the underwriting risk brief now."""
