"""
cohort_heatmap.py — Componente: Heatmap de Cohortes
====================================================
Tab 2: Cohort Retention
- Heatmap interactivo con Plotly (cohorte vs período, verde→rojo)
- Line chart: curvas de retención superpuestas por cohort
- Comparativa: mejor cohort vs peor cohort
"""

from typing import Dict, Any, Optional

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np


def render_cohort_heatmap(cohort_df: pd.DataFrame) -> None:
    """
    Renderiza el heatmap de retención por cohortes.

    Parameters
    ----------
    cohort_df : pd.DataFrame
        Matriz de cohortes con cohort_month como columna y M+N como columnas de valores.
    """
    if cohort_df.empty:
        st.warning("No hay datos de cohortes disponibles.")
        return

    # Preparar datos para el heatmap
    cohort_df = cohort_df.set_index("cohort_month")

    # Obtener solo columnas M+N
    period_cols = [c for c in cohort_df.columns if c.startswith("M+")]

    # Matriz de valores
    z_data = cohort_df[period_cols].values
    x_labels = period_cols
    y_labels = cohort_df.index.tolist()

    # Crear heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=x_labels,
            y=y_labels,
            colorscale=[
                [0.0, "#ff4444"],      # Rojo (baja retención)
                [0.3, "#ff8c42"],      # Naranja
                [0.5, "#ffd93d"],      # Amarillo
                [0.7, "#64ffda"],      # Verde claro
                [1.0, "#00c853"],      # Verde (alta retención)
            ],
            text=np.where(
                np.isnan(z_data) | (z_data == 0),
                "",
                np.char.add(np.round(z_data, 1).astype(str), "%"),
            ),
            texttemplate="%{text}",
            textfont=dict(size=10, color="white"),
            hovertemplate=(
                "Cohorte: %{y}<br>"
                "Período: %{x}<br>"
                "Retención: %{z:.1f}%<br>"
                "<extra></extra>"
            ),
            colorbar=dict(
                title=dict(text="Retención %", font=dict(color="white")),
                tickfont=dict(color="white"),
            ),
        )
    )

    fig.update_layout(
        title="Matriz de Retención por Cohorte Mensual",
        xaxis_title="Período (meses desde primera compra)",
        yaxis_title="Cohorte (mes de primera compra)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(400, len(y_labels) * 25),
        margin=dict(l=80, r=20, t=50, b=50),
        yaxis=dict(autorange="reversed"),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_retention_curves(cohort_df: pd.DataFrame) -> None:
    """
    Renderiza las curvas de retención superpuestas por cohort.

    Parameters
    ----------
    cohort_df : pd.DataFrame
        Matriz de cohortes.
    """
    if cohort_df.empty:
        return

    cohort_df = cohort_df.set_index("cohort_month")
    period_cols = [c for c in cohort_df.columns if c.startswith("M+")]

    fig = go.Figure()

    # Seleccionar un subconjunto de cohortes para legibilidad
    cohortes = cohort_df.index.tolist()
    # Si hay muchas, mostrar cada 3
    if len(cohortes) > 10:
        cohortes_mostrar = cohortes[::3]
    else:
        cohortes_mostrar = cohortes

    # Paleta de colores vibrantes
    colors = px.colors.qualitative.Set2

    for i, cohort in enumerate(cohortes_mostrar):
        valores = cohort_df.loc[cohort, period_cols].values
        # Filtrar valores válidos (no NaN, no 0 después del primer 0)
        periodos_num = list(range(len(valores)))

        color = colors[i % len(colors)]

        fig.add_trace(
            go.Scatter(
                x=periodos_num,
                y=valores,
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
            )
        )

    fig.update_layout(
        title="Curvas de Retención por Cohorte",
        xaxis_title="Meses desde primera compra",
        yaxis_title="Retención (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=450,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        legend=dict(
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0.3)",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_cohort_comparison(insights: Dict[str, Any]) -> None:
    """
    Renderiza la comparación entre mejor y peor cohorte.

    Parameters
    ----------
    insights : Dict
        Insights de cohortes con mejor/peor cohort M+3.
    """
    cohort_data = insights.get("cohort_insights", {})

    col1, col2, col3 = st.columns(3)

    mejor = cohort_data.get("mejor_cohort_m3", {})
    peor = cohort_data.get("peor_cohort_m3", {})
    cliff = cohort_data.get("churn_cliff", {})

    with col1:
        if mejor:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #0d3b2e, #1a1a2e);
                            border-radius: 12px; padding: 20px; text-align: center;
                            border: 1px solid #00c853;">
                    <p style="color: #a8b2d1; font-size: 14px; margin: 0;">🏆 Mejor Cohorte (M+3)</p>
                    <h3 style="color: #64ffda; margin: 8px 0;">{mejor.get('cohort', 'N/A')}</h3>
                    <p style="color: #00c853; font-size: 18px; margin: 0;">
                        {mejor.get('retencion_pct', 0):.1f}% retención
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No hay datos suficientes para M+3")

    with col2:
        if peor:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #3b0d0d, #1a1a2e);
                            border-radius: 12px; padding: 20px; text-align: center;
                            border: 1px solid #ff4444;">
                    <p style="color: #a8b2d1; font-size: 14px; margin: 0;">📉 Peor Cohorte (M+3)</p>
                    <h3 style="color: #ff6b6b; margin: 8px 0;">{peor.get('cohort', 'N/A')}</h3>
                    <p style="color: #ff4444; font-size: 18px; margin: 0;">
                        {peor.get('retencion_pct', 0):.1f}% retención
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No hay datos suficientes para M+3")

    with col3:
        if cliff:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #3b2e0d, #1a1a2e);
                            border-radius: 12px; padding: 20px; text-align: center;
                            border: 1px solid #ffd93d;">
                    <p style="color: #a8b2d1; font-size: 14px; margin: 0;">🪨 Churn Cliff</p>
                    <h3 style="color: #ffd93d; margin: 8px 0;">{cliff.get('periodo', 'N/A')}</h3>
                    <p style="color: #ff8c42; font-size: 18px; margin: 0;">
                        {cliff.get('drop_pct', 0):.1f}% drop
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No hay datos de churn cliff disponibles")
