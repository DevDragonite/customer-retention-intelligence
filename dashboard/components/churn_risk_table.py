"""
churn_risk_table.py — Componente: Tabla de Clientes en Riesgo
=============================================================
Tab 3: At-Risk Customers
- Tabla filtrable e interactiva
- Scatter plot: prob_churn vs revenue_total
- Botón: exportar CSV
"""

import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def render_risk_table(at_risk_df: pd.DataFrame, umbral: float = 0.6) -> None:
    """
    Renderiza la tabla filtrable de clientes en riesgo.

    Parameters
    ----------
    at_risk_df : pd.DataFrame
        DataFrame con clientes en riesgo.
    umbral : float
        Umbral de probabilidad de churn.
    """
    if at_risk_df.empty:
        st.info(f"No hay clientes con probabilidad de churn > {umbral:.0%}")
        return

    st.markdown(f"### 🚨 Clientes en Riesgo (prob > {umbral:.0%})")
    st.markdown(f"**{len(at_risk_df):,}** clientes identificados")

    # Formatear para visualización
    display_df = at_risk_df.copy()
    display_df["prob_churn"] = display_df["prob_churn"].apply(lambda x: f"{x:.1%}")
    display_df["total_revenue"] = display_df["total_revenue"].apply(lambda x: f"R$ {x:,.2f}")

    # Renombrar columnas para el display
    rename_map = {
        "customer_unique_id": "Cliente ID",
        "prob_churn": "Prob. Churn",
        "days_since_last_purchase": "Días sin compra",
        "total_revenue": "Revenue Total",
        "total_orders": "Órdenes",
        "avg_review_score": "⭐ Review",
        "customer_state": "Estado",
        "accion_recomendada": "Acción Recomendada",
    }

    cols_display = [c for c in rename_map.keys() if c in display_df.columns]
    display_df = display_df[cols_display].rename(columns=rename_map)

    # Mostrar tabla interactiva
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
    )

    # Botón de exportar CSV
    csv_data = at_risk_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Exportar CSV para Customer Success",
        data=csv_data,
        file_name="clientes_en_riesgo.csv",
        mime="text/csv",
        type="primary",
    )


def render_risk_scatter(predictions_df: pd.DataFrame, umbral: float = 0.6) -> None:
    """
    Renderiza el scatter plot: prob_churn vs revenue_total.
    Prioriza intervenciones por valor del cliente.

    Parameters
    ----------
    predictions_df : pd.DataFrame
        DataFrame con predicciones de todos los clientes.
    umbral : float
        Umbral para clasificar como en riesgo.
    """
    if predictions_df.empty:
        return

    df = predictions_df.copy()

    # Clasificar clientes
    df["segmento"] = "Bajo riesgo"
    df.loc[df["prob_churn"] > umbral, "segmento"] = "Alto riesgo"
    df.loc[
        (df["prob_churn"] > umbral) & (df["total_revenue"] > df["total_revenue"].quantile(0.75)),
        "segmento",
    ] = "⚠️ Alto valor + Alto riesgo"

    color_map = {
        "Bajo riesgo": "#64ffda",
        "Alto riesgo": "#ff6b6b",
        "⚠️ Alto valor + Alto riesgo": "#ffd93d",
    }

    fig = go.Figure()

    for segmento, color in color_map.items():
        mask = df["segmento"] == segmento
        subset = df[mask]
        if len(subset) == 0:
            continue

        fig.add_trace(
            go.Scatter(
                x=subset["prob_churn"],
                y=subset["total_revenue"],
                mode="markers",
                name=segmento,
                marker=dict(
                    color=color,
                    size=6,
                    opacity=0.6,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    "<b>Cliente:</b> %{customdata[0]}<br>"
                    "Prob. Churn: %{x:.1%}<br>"
                    "Revenue: R$ %{y:,.2f}<br>"
                    "Estado: %{customdata[1]}<br>"
                    "<extra></extra>"
                ),
                customdata=subset[["customer_unique_id", "customer_state"]].values
                if "customer_unique_id" in subset.columns and "customer_state" in subset.columns
                else None,
            )
        )

    # Línea de umbral
    fig.add_vline(
        x=umbral,
        line_dash="dash",
        line_color="#ffd93d",
        annotation_text=f"Umbral: {umbral:.0%}",
        annotation_position="top right",
        annotation_font_color="#ffd93d",
    )

    fig.update_layout(
        title="Priorización: Probabilidad de Churn vs Revenue",
        xaxis_title="Probabilidad de Churn",
        yaxis_title="Revenue Total (R$)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        margin=dict(l=60, r=20, t=50, b=50),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            tickformat=".0%",
        ),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        legend=dict(
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0.3)",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Insight automático
    alto_valor_riesgo = df[df["segmento"] == "⚠️ Alto valor + Alto riesgo"]
    if len(alto_valor_riesgo) > 0:
        revenue_at_risk = alto_valor_riesgo["total_revenue"].sum()
        st.warning(
            f"⚠️ **{len(alto_valor_riesgo):,}** clientes de alto valor están en riesgo, "
            f"representando **R$ {revenue_at_risk:,.0f}** en revenue. "
            f"Prioriza su contacto inmediato."
        )
