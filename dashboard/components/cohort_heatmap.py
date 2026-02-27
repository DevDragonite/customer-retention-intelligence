"""
cohort_heatmap.py — Cohort Retention Visualizations
=====================================================
Heatmap, retention curves, and cohort comparison cards.
"""

from typing import Dict, Any

import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translations import t  # noqa: E402
from utils import apply_chart_theme, load_cohort_insights  # noqa: E402


def render_cohort_heatmap(cohort_df: pd.DataFrame) -> None:
    """Render the cohort retention heatmap with warm colorscale."""
    if cohort_df.empty:
        st.warning(t("no_data"))
        return

    df = cohort_df.set_index("cohort_month") if "cohort_month" in cohort_df.columns else cohort_df
    period_cols = [c for c in df.columns if c.startswith("M+")]
    z_data = df[period_cols].values
    x_labels = period_cols
    y_labels = df.index.tolist()

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#CD4631"],
            [0.25, "#9E6240"],
            [0.5, "#DEA47E"],
            [1.0, "#81ADC8"],
        ],
        text=np.where(
            np.isnan(z_data) | (z_data == 0),
            "",
            np.char.add(np.round(z_data, 1).astype(str), "%"),
        ),
        texttemplate="%{text}",
        textfont=dict(size=10, color="#2E1F14"),
        hovertemplate=(
            "Cohorte: %{y}<br>"
            "Período: %{x}<br>"
            "Retención: %{z:.1f}%<br>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title=dict(text=t("cohort_retention_pct"), font=dict(color="#2E1F14")),
            tickfont=dict(color="#2E1F14"),
        ),
    ))

    fig = apply_chart_theme(fig, t("chart_cohort_heatmap"))
    fig.update_layout(
        height=max(400, len(y_labels) * 25),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_retention_curves(cohort_df: pd.DataFrame) -> None:
    """Render overlaid retention curves by cohort."""
    if cohort_df.empty:
        return

    df = cohort_df.set_index("cohort_month") if "cohort_month" in cohort_df.columns else cohort_df
    period_cols = [c for c in df.columns if c.startswith("M+")]

    fig = go.Figure()
    cohortes = df.index.tolist()
    if len(cohortes) > 10:
        cohortes = cohortes[::3]

    palette = ["#9E6240", "#DEA47E", "#CD4631", "#81ADC8", "#7D4E32",
               "#C48B65", "#A83828", "#6A96B1", "#D4956B", "#5A8FA8"]

    for i, cohort in enumerate(cohortes):
        vals = df.loc[cohort, period_cols].values
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=list(range(len(vals))),
            y=vals,
            mode="lines+markers",
            name=str(cohort),
            line=dict(width=2, color=color),
            marker=dict(size=5, color=color),
            hovertemplate=(
                f"<b>Cohorte: {cohort}</b><br>"
                "Período: M+%{x}<br>"
                "Retención: %{y:.1f}%<br>"
                "<extra></extra>"
            ),
        ))

    fig = apply_chart_theme(fig, t("chart_retention_curves"))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_cohort_comparison(insights: Dict[str, Any]) -> None:
    """Render best/worst cohort comparison in white cards."""
    cohort_data = insights.get("cohort_insights", {})
    if not cohort_data:
        cohort_data = load_cohort_insights() or {}

    mejor = cohort_data.get("mejor_cohort_m3", {})
    peor = cohort_data.get("peor_cohort_m3", {})
    cliff = cohort_data.get("churn_cliff", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        if mejor:
            st.markdown(f"""
            <div class="content-card" style="text-align:center;">
                <p style="color:#8A7A6A;font-size:0.82rem;margin:0;">{t("cohort_best")}</p>
                <h3 style="color:#81ADC8;margin:8px 0;">{mejor.get('cohort','N/A')}</h3>
                <p style="color:#81ADC8;font-size:1.2rem;margin:0;font-weight:700;">
                    {mejor.get('retencion_pct',0):.1f}% {t("cohort_retention_pct")}
                </p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if peor:
            st.markdown(f"""
            <div class="content-card" style="text-align:center;">
                <p style="color:#8A7A6A;font-size:0.82rem;margin:0;">{t("cohort_worst")}</p>
                <h3 style="color:#CD4631;margin:8px 0;">{peor.get('cohort','N/A')}</h3>
                <p style="color:#CD4631;font-size:1.2rem;margin:0;font-weight:700;">
                    {peor.get('retencion_pct',0):.1f}% {t("cohort_retention_pct")}
                </p>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        if cliff:
            st.markdown(f"""
            <div class="content-card" style="text-align:center;">
                <p style="color:#8A7A6A;font-size:0.82rem;margin:0;">{t("cohort_cliff")}</p>
                <h3 style="color:#9E6240;margin:8px 0;">{cliff.get('periodo','N/A')}</h3>
                <p style="color:#9E6240;font-size:1.2rem;margin:0;font-weight:700;">
                    {cliff.get('drop_pct',0):.1f}% {t("cohort_drop")}
                </p>
            </div>
            """, unsafe_allow_html=True)
