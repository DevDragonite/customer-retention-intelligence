"""
kpi_cards.py — Componente: KPI Cards + Gráficos de Overview
===========================================================
Tab 1: Executive Overview
- 4 tarjetas KPI
- Gráfico de línea: evolución mensual del churn rate
- Barras horizontales: top 10 estados por churn rate
"""

from typing import Dict, Any

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd


def render_kpi_cards(kpis: Dict[str, Any]) -> None:
    """Renderiza las 4 tarjetas KPI principales."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border-radius: 12px; padding: 20px; text-align: center;
                        border: 1px solid #0f3460;">
                <p style="color: #a8b2d1; font-size: 14px; margin: 0;">Total Clientes</p>
                <h2 style="color: #64ffda; margin: 8px 0;">{kpis['total_clientes']:,}</h2>
                <p style="color: #8892b0; font-size: 12px; margin: 0;">
                    {kpis['clientes_activos']:,} activos · {kpis['clientes_churned']:,} churned
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        churn_color = "#ff6b6b" if kpis["churn_rate"] > 50 else "#ffd93d"
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border-radius: 12px; padding: 20px; text-align: center;
                        border: 1px solid #0f3460;">
                <p style="color: #a8b2d1; font-size: 14px; margin: 0;">Tasa de Churn</p>
                <h2 style="color: {churn_color}; margin: 8px 0;">{kpis['churn_rate']:.1f}%</h2>
                <p style="color: #8892b0; font-size: 12px; margin: 0;">
                    Últimos 180 días
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border-radius: 12px; padding: 20px; text-align: center;
                        border: 1px solid #0f3460;">
                <p style="color: #a8b2d1; font-size: 14px; margin: 0;">Revenue en Riesgo</p>
                <h2 style="color: #ff6b6b; margin: 8px 0;">R$ {kpis['revenue_en_riesgo']:,.0f}</h2>
                <p style="color: #8892b0; font-size: 12px; margin: 0;">
                    {kpis['clientes_en_riesgo_predicho']:,} clientes predichos
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border-radius: 12px; padding: 20px; text-align: center;
                        border: 1px solid #0f3460;">
                <p style="color: #a8b2d1; font-size: 14px; margin: 0;">LTV Promedio</p>
                <h2 style="color: #64ffda; margin: 8px 0;">R$ {kpis['ltv_promedio']:,.0f}</h2>
                <p style="color: #8892b0; font-size: 12px; margin: 0;">
                    ⭐ {kpis['avg_review_score']:.1f} review promedio
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_churn_trend(evolucion: list) -> None:
    """Renderiza el gráfico de evolución mensual del churn rate."""
    if not evolucion:
        st.warning("No hay datos de evolución disponibles.")
        return

    df = pd.DataFrame(evolucion)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["mes"],
            y=df["churn_rate"],
            mode="lines+markers",
            name="Churn Rate",
            line=dict(color="#ff6b6b", width=3),
            marker=dict(size=8, color="#ff6b6b"),
            fill="tozeroy",
            fillcolor="rgba(255, 107, 107, 0.1)",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Churn Rate: %{y:.1f}%<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Evolución Mensual del Churn Rate",
        xaxis_title="Mes",
        yaxis_title="Churn Rate (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_top_estados(churn_por_estado: Dict[str, Dict]) -> None:
    """Renderiza las barras horizontales: top 10 estados por churn rate."""
    if not churn_por_estado:
        st.warning("No hay datos de estados disponibles.")
        return

    # Convertir a DataFrame y tomar top 10
    data = []
    for estado, vals in churn_por_estado.items():
        data.append({
            "Estado": estado,
            "Churn Rate (%)": vals["churn_rate"],
            "Total Clientes": vals["total"],
        })

    df = pd.DataFrame(data).nlargest(10, "Churn Rate (%)")
    df = df.sort_values("Churn Rate (%)", ascending=True)  # Para barras horizontales

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Churn Rate (%)"],
            y=df["Estado"],
            orientation="h",
            marker=dict(
                color=df["Churn Rate (%)"],
                colorscale=[[0, "#64ffda"], [0.5, "#ffd93d"], [1, "#ff6b6b"]],
                line=dict(width=0),
            ),
            text=[f"{v:.1f}%" for v in df["Churn Rate (%)"]],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Churn Rate: %{x:.1f}%<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Top 10 Estados por Churn Rate",
        xaxis_title="Churn Rate (%)",
        yaxis_title="",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=60, r=40, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
