"""
kpi_cards.py — Executive Overview KPIs & Charts
=================================================
Renders glass-card KPIs, churn trend, and top states chart.
"""

from typing import Dict, Any

import plotly.graph_objects as go
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translations import t  # noqa: E402
from utils import apply_chart_theme  # noqa: E402


def render_kpi_cards(insights: Dict[str, Any]) -> None:
    """Render the 4 executive KPIs inside a glass card."""
    kpis = insights.get("kpis", {})
    total = kpis.get("total_clientes", 0)
    churn_rate = kpis.get("tasa_churn", 0)
    revenue_risk = kpis.get("revenue_en_riesgo", 0)
    ltv = kpis.get("ltv_promedio", 0)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t("kpi_total_customers"), f"{total:,}")
    with col2:
        st.metric(t("kpi_churn_rate"), f"{churn_rate:.1f}%")
    with col3:
        if revenue_risk >= 1_000_000:
            val = f"R$ {revenue_risk / 1_000_000:.1f}M"
        else:
            val = f"R$ {revenue_risk:,.0f}"
        st.metric(t("kpi_revenue_at_risk"), val)
    with col4:
        st.metric(t("kpi_avg_ltv"), f"R$ {ltv:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_churn_trend(insights: Dict[str, Any]) -> None:
    """Render monthly churn rate evolution line chart."""
    evolucion = insights.get("evolucion_churn", {})
    if not evolucion:
        return

    meses = list(evolucion.keys())
    valores = [v.get("churn_rate", 0) if isinstance(v, dict) else v for v in evolucion.values()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses,
        y=valores,
        mode="lines+markers",
        line=dict(color="#CD4631", width=3),
        marker=dict(size=8, color="#DEA47E", line=dict(width=2, color="#CD4631")),
        fill="tozeroy",
        fillcolor="rgba(205,70,49,0.1)",
        hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<extra></extra>",
    ))
    fig = apply_chart_theme(fig, t("chart_churn_trend"))
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)


def render_top_states(insights: Dict[str, Any]) -> None:
    """Render top 10 states by churn rate horizontal bar chart."""
    churn_estado = insights.get("churn_por_estado", {})
    if not churn_estado:
        return

    data = sorted(
        [(k, v["churn_rate"] if isinstance(v, dict) else v) for k, v in churn_estado.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    estados = [d[0] for d in reversed(data)]
    rates = [d[1] for d in reversed(data)]

    colors = ["#CD4631" if r > 60 else "#DEA47E" if r > 50 else "#81ADC8" for r in rates]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rates,
        y=estados,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x:.1f}%<extra></extra>",
    ))
    fig = apply_chart_theme(fig, t("chart_churn_by_state"))
    fig.update_layout(height=380, yaxis=dict(tickfont=dict(size=11)))
    st.plotly_chart(fig, use_container_width=True)
