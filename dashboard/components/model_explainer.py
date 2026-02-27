"""
model_explainer.py — Componente: Explicabilidad del Modelo
==========================================================
Tab 4: Model Explainer
- SHAP waterfall chart para cliente seleccionado
- Feature importance global (barras horizontales)
- Texto generado automáticamente
"""

from typing import Dict, Any, Optional, List

import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np


def render_feature_importance(metrics: Dict[str, Any]) -> None:
    """
    Renderiza el gráfico de importancia global de features.

    Parameters
    ----------
    metrics : Dict
        Métricas del modelo con feature_importance.
    """
    importance = metrics.get("feature_importance", {})
    if not importance:
        st.warning("No hay datos de importancia de features disponibles.")
        return

    # Ordenar por importancia
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    features = [f[0] for f in sorted_features]
    values = [f[1] for f in sorted_features]

    # Nombres más legibles
    nombres_legibles = {
        "days_since_last_purchase": "Días desde última compra",
        "days_since_first_purchase": "Días desde primera compra",
        "customer_tenure_days": "Antigüedad (días)",
        "total_orders": "Total de órdenes",
        "avg_days_between_orders": "Prom. días entre órdenes",
        "orders_last_30d": "Órdenes últimos 30d",
        "orders_last_60d": "Órdenes últimos 60d",
        "orders_last_90d": "Órdenes últimos 90d",
        "total_revenue": "Revenue total",
        "avg_order_value": "Valor promedio de orden",
        "max_order_value": "Valor máximo de orden",
        "revenue_trend": "Tendencia de revenue",
        "avg_review_score": "Review promedio",
        "last_review_score": "Último review",
        "pct_reviews_below_3": "% reviews < 3",
        "has_negative_review": "Tiene review negativo",
        "review_score_trend": "Tendencia de reviews",
        "avg_delivery_days": "Días promedio entrega",
        "delivery_delay_rate": "Tasa de retrasos",
        "avg_delay_days": "Promedio días retraso",
    }

    display_names = [nombres_legibles.get(f, f) for f in features]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=values,
            y=display_names,
            orientation="h",
            marker=dict(
                color=values,
                colorscale=[[0, "#0f3460"], [0.5, "#64ffda"], [1, "#00c853"]],
                line=dict(width=0),
            ),
            text=[f"{v:.4f}" for v in values],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Importancia: %{x:.4f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Importancia Global de Features (SHAP)",
        xaxis_title="Importancia Media |SHAP|",
        yaxis_title="",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(400, len(features) * 28),
        margin=dict(l=200, r=60, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_shap_waterfall(
    shap_df: Optional[pd.DataFrame],
    predictions_df: pd.DataFrame,
    feature_columns: List[str],
    selected_customer: Optional[str] = None,
) -> None:
    """
    Renderiza el SHAP waterfall chart para un cliente seleccionado.

    Parameters
    ----------
    shap_df : pd.DataFrame or None
        SHAP values por cliente.
    predictions_df : pd.DataFrame
        Predicciones con prob_churn.
    feature_columns : list
        Lista de columnas de features.
    selected_customer : str or None
        ID del cliente seleccionado.
    """
    if shap_df is None or shap_df.empty:
        st.info("ℹ️ Los SHAP values no están disponibles. Ejecuta el pipeline con SHAP instalado.")
        return

    if selected_customer is None:
        st.info("👆 Selecciona un cliente para ver su explicación detallada.")
        return

    # Buscar SHAP values del cliente
    customer_shap = shap_df[shap_df["customer_unique_id"] == selected_customer]

    if customer_shap.empty:
        st.warning(f"No hay SHAP values disponibles para el cliente {selected_customer[:12]}...")
        return

    # Extraer valores SHAP
    shap_cols = [c for c in customer_shap.columns if c.startswith("shap_")]
    valores_shap = customer_shap[shap_cols].values[0]
    nombres = [c.replace("shap_", "") for c in shap_cols]

    # Nombres legibles
    nombres_legibles = {
        "days_since_last_purchase": "Días sin compra",
        "days_since_first_purchase": "Antigüedad",
        "customer_tenure_days": "Tenure",
        "total_orders": "Total órdenes",
        "avg_days_between_orders": "Días entre órdenes",
        "orders_last_30d": "Órdenes 30d",
        "orders_last_60d": "Órdenes 60d",
        "orders_last_90d": "Órdenes 90d",
        "total_revenue": "Revenue",
        "avg_order_value": "Valor prom. orden",
        "max_order_value": "Valor máx. orden",
        "revenue_trend": "Tendencia revenue",
        "avg_review_score": "Review prom.",
        "last_review_score": "Último review",
        "pct_reviews_below_3": "% reviews < 3",
        "has_negative_review": "Review negativo",
        "review_score_trend": "Tendencia reviews",
        "avg_delivery_days": "Días entrega",
        "delivery_delay_rate": "Tasa retrasos",
        "avg_delay_days": "Días retraso",
    }

    display_names = [nombres_legibles.get(n, n) for n in nombres]

    # Ordenar por valor absoluto (top 10)
    indices = np.argsort(np.abs(valores_shap))[::-1][:10]
    top_names = [display_names[i] for i in indices]
    top_values = [valores_shap[i] for i in indices]

    # Colores: rojo si empuja hacia churn, verde si retiene
    colors = ["#ff6b6b" if v > 0 else "#64ffda" for v in top_values]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top_values,
            y=top_names,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{v:+.3f}" for v in top_values],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "SHAP: %{x:+.4f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"SHAP — Factores del Cliente {selected_customer[:12]}...",
        xaxis_title="Impacto en predicción (SHAP value)",
        yaxis_title="",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=150, r=60, t=50, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zeroline=True, zerolinecolor="white"),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Leyenda de colores
    st.markdown(
        "🔴 **Rojo** = empuja hacia churn &nbsp;&nbsp; "
        "🟢 **Verde** = retiene al cliente"
    )


def render_auto_explanation(
    predictions_df: pd.DataFrame,
    selected_customer: Optional[str] = None,
) -> None:
    """
    Genera texto explicativo automático para el cliente seleccionado.

    Parameters
    ----------
    predictions_df : pd.DataFrame
        Predicciones con features.
    selected_customer : str or None
        ID del cliente.
    """
    if selected_customer is None:
        return

    customer = predictions_df[predictions_df["customer_unique_id"] == selected_customer]
    if customer.empty:
        return

    row = customer.iloc[0]
    prob = row.get("prob_churn", 0)
    dias = row.get("days_since_last_purchase", 0)
    revenue = row.get("total_revenue", 0)
    review = row.get("avg_review_score", 0)
    orders = row.get("total_orders", 0)

    # Determinar nivel de riesgo
    if prob > 0.85:
        nivel = "🚨 CRÍTICO"
        color = "#ff4444"
    elif prob > 0.6:
        nivel = "⚠️ ALTO"
        color = "#ff6b6b"
    elif prob > 0.4:
        nivel = "🔶 MODERADO"
        color = "#ffd93d"
    else:
        nivel = "✅ BAJO"
        color = "#64ffda"

    # Generar razones
    razones = []
    if dias > 120:
        razones.append(f"lleva **{int(dias)} días** sin realizar una compra")
    if review < 3:
        razones.append(f"su review promedio es bajo (**{review:.1f}⭐**)")
    if orders <= 1:
        razones.append("solo realizó **1 compra** (sin re-compra)")
    if revenue < 100:
        razones.append(f"su gasto total es bajo (**R$ {revenue:.0f}**)")

    razones_texto = ", ".join(razones) if razones else "su patrón de comportamiento general"

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                    border-radius: 12px; padding: 20px;
                    border-left: 4px solid {color};">
            <h4 style="color: {color}; margin: 0 0 10px 0;">
                Riesgo {nivel}
            </h4>
            <p style="color: #ccd6f6; font-size: 16px; line-height: 1.6;">
                Este cliente tiene un <b>{prob:.0%}</b> de probabilidad de churn
                porque {razones_texto}.
            </p>
            <p style="color: #8892b0; font-size: 14px;">
                📈 Revenue histórico: R$ {revenue:,.0f} · 
                🛒 {int(orders)} órdenes · 
                ⭐ {review:.1f} review promedio
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_model_metrics(metrics: Dict[str, Any]) -> None:
    """Renderiza las métricas del modelo en cards."""
    test_metrics = metrics.get("resultados_test", {})
    nombre_modelo = metrics.get("mejor_modelo", "N/A")
    threshold = metrics.get("threshold_optimo", "N/A")

    st.markdown(f"### 🤖 Modelo: {nombre_modelo} (threshold: {threshold})")

    col1, col2, col3, col4 = st.columns(4)

    metric_data = [
        ("AUC-ROC", test_metrics.get("auc", 0), "#64ffda"),
        ("F1-Score", test_metrics.get("f1", 0), "#ffd93d"),
        ("Precisión", test_metrics.get("precision", 0), "#ff8c42"),
        ("Recall", test_metrics.get("recall", 0), "#ff6b6b"),
    ]

    for col, (name, val, color) in zip([col1, col2, col3, col4], metric_data):
        with col:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                            border-radius: 12px; padding: 15px; text-align: center;
                            border: 1px solid #0f3460;">
                    <p style="color: #a8b2d1; font-size: 13px; margin: 0;">{name}</p>
                    <h3 style="color: {color}; margin: 5px 0;">{val:.2%}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
