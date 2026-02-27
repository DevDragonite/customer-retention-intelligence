"""
geo_map.py — Geographic Intelligence
======================================
Brazil bubble map and delivery delay vs churn correlation scatter.
Colors updated for cream background.
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
from utils import apply_chart_theme  # noqa: E402

COORDS = {
    "AC": (-8.77, -70.55), "AL": (-9.71, -35.73), "AM": (-3.07, -61.66),
    "AP": (1.41, -51.77), "BA": (-12.96, -38.51), "CE": (-3.71, -38.54),
    "DF": (-15.83, -47.86), "ES": (-19.19, -40.34), "GO": (-16.64, -49.31),
    "MA": (-2.53, -44.28), "MG": (-18.10, -44.38), "MS": (-20.51, -54.54),
    "MT": (-12.64, -55.42), "PA": (-5.53, -52.29), "PB": (-7.06, -35.55),
    "PE": (-8.28, -35.07), "PI": (-8.28, -43.68), "PR": (-24.89, -51.55),
    "RJ": (-22.84, -43.15), "RN": (-5.22, -36.52), "RO": (-11.22, -62.80),
    "RR": (1.89, -61.22), "RS": (-30.01, -51.22), "SC": (-27.33, -49.44),
    "SE": (-10.90, -37.07), "SP": (-23.55, -46.64), "TO": (-10.25, -48.25),
}

ESTADOS_BRASIL = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins",
}


def render_churn_map(predictions_df: pd.DataFrame, churn_por_estado: Dict) -> None:
    """Render Brazil bubble map with churn rate by state."""
    if not churn_por_estado:
        st.warning(t("no_data"))
        return

    data = []
    for estado, vals in churn_por_estado.items():
        lat, lon = COORDS.get(estado, (0, 0))
        data.append({
            "estado": estado,
            "nombre": ESTADOS_BRASIL.get(estado, estado),
            "churn_rate": vals["churn_rate"],
            "total": vals["total"],
            "churned": vals["churned"],
            "lat": lat, "lon": lon,
        })

    df = pd.DataFrame(data)

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=df["lat"], lon=df["lon"],
        text=df.apply(
            lambda r: (
                f"<b>{r['nombre']} ({r['estado']})</b><br>"
                f"Churn: {r['churn_rate']:.1f}%<br>"
                f"Total: {r['total']:,}<br>"
                f"Churned: {r['churned']:,}"
            ), axis=1,
        ),
        hoverinfo="text",
        marker=dict(
            size=df["total"] / df["total"].max() * 40 + 10,
            color=df["churn_rate"],
            colorscale=[[0, "#81ADC8"], [0.5, "#DEA47E"], [1, "#CD4631"]],
            colorbar=dict(
                title=dict(text="Churn %", font=dict(color="#2E1F14")),
                tickfont=dict(color="#2E1F14"),
            ),
            line=dict(width=1, color="rgba(158,98,64,0.3)"),
            opacity=0.85,
        ),
    ))

    fig.update_geos(
        scope="south america",
        showland=True, landcolor="#F5EDD6",
        showocean=True, oceancolor="#E8DCC0",
        showcountries=True, countrycolor="rgba(158,98,64,0.3)",
        showcoastlines=True, coastlinecolor="rgba(158,98,64,0.3)",
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
        lonaxis=dict(range=[-75, -30]),
        lataxis=dict(range=[-35, 6]),
    )

    fig = apply_chart_theme(fig, t("chart_geo_map"))
    fig.update_layout(height=550, showlegend=False, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)


def render_delivery_vs_churn(features_df: pd.DataFrame) -> None:
    """Render delivery delay vs churn rate scatter by state."""
    if features_df.empty:
        return

    estado_stats = (
        features_df.groupby("customer_state")
        .agg(
            avg_delivery_days=("avg_delivery_days", "mean"),
            delivery_delay_rate=("delivery_delay_rate", "mean"),
            churn_rate=("churned", "mean"),
            n_clientes=("customer_unique_id", "count"),
        )
        .reset_index()
    )

    estado_stats["churn_pct"] = estado_stats["churn_rate"] * 100
    estado_stats["delay_pct"] = estado_stats["delivery_delay_rate"] * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=estado_stats["delay_pct"], y=estado_stats["churn_pct"],
        mode="markers+text",
        text=estado_stats["customer_state"],
        textposition="top center",
        textfont=dict(size=10, color="#2E1F14"),
        marker=dict(
            size=estado_stats["n_clientes"] / estado_stats["n_clientes"].max() * 40 + 8,
            color=estado_stats["churn_pct"],
            colorscale=[[0, "#81ADC8"], [0.5, "#DEA47E"], [1, "#CD4631"]],
            line=dict(width=1, color="rgba(158,98,64,0.2)"),
            opacity=0.8,
        ),
        customdata=estado_stats[["customer_state", "n_clientes"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>Delay: %{x:.1f}%<br>"
            "Churn: %{y:.1f}%<br>Clientes: %{customdata[1]:,}<extra></extra>"
        ),
    ))

    if len(estado_stats) > 2:
        z = np.polyfit(estado_stats["delay_pct"], estado_stats["churn_pct"], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(estado_stats["delay_pct"].min(), estado_stats["delay_pct"].max(), 50)
        fig.add_trace(go.Scatter(
            x=x_trend, y=p(x_trend),
            mode="lines", line=dict(color="#9E6240", dash="dash", width=2),
            name="Trend", showlegend=True,
        ))
        corr = estado_stats["delay_pct"].corr(estado_stats["churn_pct"])
        st.markdown(f"📊 **{t('geo_correlation')}:** **{corr:.2f}**")

    fig = apply_chart_theme(fig, t("chart_delivery_vs_churn"))
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
