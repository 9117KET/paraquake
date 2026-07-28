"""ParaQuake -- Streamlit demo UI.

Run locally with:  streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
from dotenv import load_dotenv

from components.map_view import build_deck
from components.metrics import render_summary_metrics
from components.tables import portfolio_dataframe, trigger_results_dataframe

load_dotenv()

from paraquake.agents.graph import run_pipeline  # noqa: E402  (after sys.path insert)

st.set_page_config(page_title="ParaQuake", page_icon="\U0001f30f", layout="wide")

PRESETS = {
    "Haiti, 12 Jan 2010 (real M7.0, CCRIF's landmark payout)": {
        "start_date": "2010-01-12",
        "end_date": "2010-01-13",
        "min_magnitude": 5.0,
        "use_offline_fixture": False,
    },
    "Turkiye-Syria, 6 Feb 2023 (real M7.8, bundled offline fixture)": {
        "start_date": "2023-02-06",
        "end_date": "2023-02-07",
        "min_magnitude": 5.0,
        "use_offline_fixture": True,
    },
}

st.title("ParaQuake")
st.caption(
    "A parametric earthquake NatCat trigger engine and AI underwriting-brief agent. "
    "Real USGS earthquake data, a synthetic exposure portfolio, transparent geospatial "
    "trigger logic, and a LangGraph agent pipeline."
)
st.warning(
    "**Educational demo, not an actuarial model.** The attenuation formula, trigger tiers, "
    "and exposure portfolio are simplified/synthetic for demonstration purposes. See the "
    "Methodology tab for full limitations.",
    icon="⚠️",
)

with st.sidebar:
    st.header("Run configuration")

    preset_choice = st.selectbox("Case study preset", ["Custom"] + list(PRESETS.keys()))

    if preset_choice != "Custom":
        preset = PRESETS[preset_choice]
        start_date = datetime.date.fromisoformat(preset["start_date"])
        end_date = datetime.date.fromisoformat(preset["end_date"])
        min_magnitude = preset["min_magnitude"]
        use_offline_fixture = preset["use_offline_fixture"]
    else:
        start_date = st.date_input("Start date", datetime.date.today() - datetime.timedelta(days=90))
        end_date = st.date_input("End date", datetime.date.today())
        min_magnitude = st.slider("Minimum magnitude", 4.0, 8.5, 5.0, 0.1)
        use_offline_fixture = st.checkbox("Use bundled offline fixture instead of a live USGS query", value=False)

    run_clicked = st.button("Run analysis", type="primary")

if run_clicked:
    try:
        with st.spinner("Fetching hazard data, evaluating triggers, generating brief..."):
            final_state = run_pipeline(
                start_date=str(start_date),
                end_date=str(end_date),
                min_magnitude=min_magnitude,
                use_offline_fixture=use_offline_fixture,
            )
        st.session_state["final_state"] = final_state
    except Exception as exc:  # noqa: BLE001 -- surfaced directly to the user
        st.error(
            f"Pipeline run failed: {exc}\n\n"
            "If this mentions GROQ_API_KEY, set it in `.env` (local) or in your "
            "Streamlit Cloud app secrets."
        )

state = st.session_state.get("final_state")

tab_map, tab_portfolio, tab_results, tab_brief, tab_about = st.tabs(
    ["Map", "Portfolio", "Trigger Results", "AI Underwriting Brief", "Methodology"]
)

with tab_map:
    if state:
        deck = build_deck(state["portfolio"], state["events"], state["trigger_results"])
        st.pydeck_chart(deck)
        render_summary_metrics(state["portfolio_summary"])
    else:
        st.info("Choose a case study preset (or custom dates) in the sidebar, then click **Run analysis**.")

with tab_portfolio:
    if state:
        st.dataframe(portfolio_dataframe(state["portfolio"], state["trigger_results"]), use_container_width=True)
    else:
        st.info("Run an analysis to see live site-by-site status.")

with tab_results:
    if state:
        df = trigger_results_dataframe(state["trigger_results"])
        if df.empty:
            st.info("No sites were triggered for this event window.")
        else:
            st.dataframe(df, use_container_width=True)
            render_summary_metrics(state["portfolio_summary"])
    else:
        st.info("Run an analysis to see trigger results.")

with tab_brief:
    if state:
        badge = "✅ QA passed" if state.get("qa_passed") else "⚠️ QA flagged an issue"
        st.markdown(f"**{badge}**")
        if not state.get("qa_passed") and state.get("qa_notes"):
            with st.expander("QA notes"):
                for note in state["qa_notes"]:
                    st.write("-", note)
        st.markdown(state.get("report_markdown", "_No report generated._"))
        with st.expander("Traceability: numeric data the brief was grounded in"):
            st.json(state.get("portfolio_summary", {}))
    else:
        st.info("Run an analysis to generate the AI underwriting brief.")

with tab_about:
    st.markdown(
        """
### Methodology

**Hazard data**: real earthquake events from the [USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/),
no authentication required.

**Exposure portfolio**: 20 synthetic sites at real coordinates in seismically active regions
worldwide (`data/exposure_portfolio.csv`). Site names, sums insured, and trigger parameters
are illustrative -- no real insurer's policyholder data is used.

**Trigger logic ("cat-in-a-circle")**: for every (event, site) pair within the site's
`trigger_radius_km` and shallower than 70km depth, an `effective_intensity` is computed as:

    effective_intensity = magnitude - 1.5 * log10(distance_km + 1) - 0.001 * depth_km

This is a deliberately simplified attenuation shape (intensity falls off with log-distance
and depth), **not** a calibrated ground-motion prediction equation (GMPE). A production
NatCat model would use a peer-reviewed GMPE with soil/site amplification factors.

**Payout tiers**: discrete, based on how far `effective_intensity` clears the site's own
`trigger_magnitude`: 25% / 60% / 100% of the site's `max_payout_eur`, per-occurrence.

**Basis risk**: because payout is driven by a physical parameter (estimated shaking
intensity), not an on-the-ground loss assessment, a real parametric cover can pay out more
or less than actual damage -- this is a known, accepted trade-off in the real product,
made in exchange for fast, unambiguous claims settlement.

**AI underwriting brief**: a Groq-hosted Llama model, orchestrated via LangGraph, turns the
computed trigger table into a plain-English brief for both technical and non-technical
stakeholders. A QA guardrail node checks the brief for a mandatory limitations disclaimer
and cross-checks every EUR figure it mentions against the computed ground truth, retrying
once if either check fails.

### Links

- Source code: see this repo's README for the GitHub link.
- Author: Kinlo Ephriam Tangiri -- [kinloephraim.com](https://www.kinloephraim.com/)
"""
    )
