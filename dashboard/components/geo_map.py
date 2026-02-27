"""
geo_map.py — Componente: Inteligencia Geográfica
=================================================
Tab 5: Geo Intelligence
- Mapa coroplético de Brasil: intensidad de churn por estado
- Correlación: delivery delay vs churn rate por estado (scatter)
"""

from typing import Dict, Any

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np


# Mapeo de siglas de estados brasileños a nombres completos
ESTADOS_BRASIL = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais", "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins",
}


def render_churn_map(
    predictions_df: pd.DataFrame,
    churn_por_estado: Dict[str, Dict],
) -> None:
    """
    Renderiza el mapa coroplético de Brasil con intensidad de churn por estado.

    Parameters
    ----------
    predictions_df : pd.DataFrame
        Predicciones de churn.
    churn_por_estado : Dict
        Diccionario con churn rate por estado.
    """
    if not churn_por_estado:
        st.warning("No hay datos geográficos disponibles.")
        return

    # Preparar datos para el mapa
    data = []
    for estado, vals in churn_por_estado.items():
        data.append({
            "estado": estado,
            "nombre": ESTADOS_BRASIL.get(estado, estado),
            "churn_rate": vals["churn_rate"],
            "total_clientes": vals["total"],
            "churned": vals["churned"],
        })

    df = pd.DataFrame(data)

    # Crear mapa coroplético usando Plotly choropleth
    # Usamos un scatter geo como alternativa para estados brasileños
    fig = go.Figure()

    # Coordenadas aproximadas de cada estado para visualización
    coords_estados = {
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

    df["lat"] = df["estado"].map(lambda x: coords_estados.get(x, (0, 0))[0])
    df["lon"] = df["estado"].map(lambda x: coords_estados.get(x, (0, 0))[1])

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lat=df["lat"],
            lon=df["lon"],
            text=df.apply(
                lambda r: (
                    f"<b>{r['nombre']} ({r['estado']})</b><br>"
                    f"Churn Rate: {r['churn_rate']:.1f}%<br>"
                    f"Total clientes: {r['total_clientes']:,}<br>"
                    f"Churned: {r['churned']:,}"
                ),
                axis=1,
            ),
            hoverinfo="text",
            marker=dict(
                size=df["total_clientes"] / df["total_clientes"].max() * 40 + 10,
                color=df["churn_rate"],
                colorscale=[[0, "#64ffda"], [0.5, "#ffd93d"], [1, "#ff4444"]],
                colorbar=dict(
                    title=dict(text="Churn %", font=dict(color="white")),
                    tickfont=dict(color="white"),
                ),
                line=dict(width=1, color="white"),
                opacity=0.85,
            ),
        )
    )

    fig.update_geos(
        scope="south america",
        showland=True,
        landcolor="rgb(20, 20, 40)",
        showocean=True,
        oceancolor="rgb(10, 10, 30)",
        showcountries=True,
        countrycolor="rgba(255,255,255,0.2)",
        showcoastlines=True,
        coastlinecolor="rgba(255,255,255,0.2)",
        showframe=False,
        bgcolor="rgba(0,0,0,0)",
        lonaxis=dict(range=[-75, -30]),
        lataxis=dict(range=[-35, 6]),
    )

    fig.update_layout(
        title="Mapa de Churn por Estado (tamaño = vol. clientes, color = churn rate)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_delivery_vs_churn(features_df: pd.DataFrame) -> None:
    """
    Renderiza la correlación entre delivery delay y churn rate por estado.

    Parameters
    ----------
    features_df : pd.DataFrame
        Features de churn con columnas de logística.
    """
    if features_df.empty:
        return

    # Agregar por estado
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

    estado_stats["churn_rate_pct"] = estado_stats["churn_rate"] * 100
    estado_stats["delivery_delay_pct"] = estado_stats["delivery_delay_rate"] * 100
    estado_stats["nombre"] = estado_stats["customer_state"].map(
        lambda x: ESTADOS_BRASIL.get(x, x)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=estado_stats["delivery_delay_pct"],
            y=estado_stats["churn_rate_pct"],
            mode="markers+text",
            text=estado_stats["customer_state"],
            textposition="top center",
            textfont=dict(size=10, color="white"),
            marker=dict(
                size=estado_stats["n_clientes"] / estado_stats["n_clientes"].max() * 40 + 8,
                color=estado_stats["churn_rate_pct"],
                colorscale=[[0, "#64ffda"], [0.5, "#ffd93d"], [1, "#ff4444"]],
                line=dict(width=1, color="white"),
                opacity=0.8,
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Tasa de retraso: %{x:.1f}%<br>"
                "Churn rate: %{y:.1f}%<br>"
                "Clientes: %{customdata[1]:,}<br>"
                "<extra></extra>"
            ),
            customdata=estado_stats[["nombre", "n_clientes"]].values,
        )
    )

    # Línea de tendencia
    if len(estado_stats) > 2:
        z = np.polyfit(estado_stats["delivery_delay_pct"], estado_stats["churn_rate_pct"], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(
            estado_stats["delivery_delay_pct"].min(),
            estado_stats["delivery_delay_pct"].max(),
            50,
        )
        fig.add_trace(
            go.Scatter(
                x=x_trend,
                y=p(x_trend),
                mode="lines",
                line=dict(color="#ffd93d", dash="dash", width=2),
                name="Tendencia",
                showlegend=True,
            )
        )

        # Calcular correlación
        corr = estado_stats["delivery_delay_pct"].corr(estado_stats["churn_rate_pct"])
        st.markdown(
            f"📊 **Correlación** entre tasa de retraso y churn rate: **{corr:.2f}**"
        )

    fig.update_layout(
        title="Correlación: Tasa de Retraso en Entrega vs Churn Rate por Estado",
        xaxis_title="Tasa de Retraso en Entrega (%)",
        yaxis_title="Churn Rate (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        margin=dict(l=60, r=20, t=50, b=50),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0.3)"),
    )

    st.plotly_chart(fig, use_container_width=True)
