"""Renders the top-level summary metric row."""

from __future__ import annotations

import streamlit as st


def render_summary_metrics(portfolio_summary: dict) -> None:
    cols = st.columns(4)
    cols[0].metric("Sites triggered", portfolio_summary.get("sites_triggered", 0))
    cols[1].metric("Total payout (EUR)", f"{portfolio_summary.get('total_payout_eur', 0):,.0f}")
    cols[2].metric("Largest single payout (EUR)", f"{portfolio_summary.get('largest_single_payout_eur', 0):,.0f}")
    cols[3].metric("Events evaluated", portfolio_summary.get("total_events_evaluated", 0))
