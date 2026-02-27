"""
app.py — Dashboard Principal: Churn Prediction + Cohort Retention
=================================================================
Dashboard interactivo construido con Streamlit y Plotly.

5 pestañas:
  1. Executive Overview — KPIs, evolución del churn, top estados
  2. Cohort Retention — Heatmap, curvas de retención, mejor/peor cohorte
  3. At-Risk Customers — Tabla, scatter de priorización, exportar CSV
  4. Model Explainer — SHAP, importancia de features, explicación automática
  5. Geo Intelligence — Mapa coroplético, correlación delivery vs churn

Ejecución:
  streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import (
    cargar_predicciones,
    cargar_at_risk,
    cargar_features,
    cargar_cohort_matrix,
    cargar_revenue_cohort_matrix,
    cargar_insights,
    cargar_metricas,
    cargar_shap_values,
    filtrar_datos,
)
from components.kpi_cards import render_kpi_cards, render_churn_trend, render_top_estados
from components.cohort_heatmap import (
    render_cohort_heatmap,
    render_retention_curves,
    render_cohort_comparison,
)
from components.churn_risk_table import render_risk_table, render_risk_scatter
from components.model_explainer import (
    render_feature_importance,
    render_shap_waterfall,
    render_auto_explanation,
    render_model_metrics,
)
from components.geo_map import render_churn_map, render_delivery_vs_churn

# ──────────────────────────────────────────────
# Configuración de la página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Intelligence Dashboard",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CSS personalizado — Dark Theme
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Fondo principal oscuro */
    .stApp {
        background: linear-gradient(180deg, #0a0a1a 0%, #0d1117 50%, #1a1a2e 100%);
    }

    /* Sidebar oscura */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #21262d;
    }

    /* Tabs con estilo */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: rgba(13, 17, 23, 0.6);
        border-radius: 12px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #8b949e;
        padding: 10px 20px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0f3460, #16213e);
        color: #64ffda !important;
        border: 1px solid #0f3460;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #0f3460;
    }

    /* Headers */
    h1, h2, h3 {
        color: #ccd6f6 !important;
    }

    /* Texto general */
    .stMarkdown p {
        color: #8892b0;
    }

    /* DataFrames */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Botones */
    .stDownloadButton button {
        background: linear-gradient(135deg, #0f3460, #16213e) !important;
        color: #64ffda !important;
        border: 1px solid #64ffda !important;
        border-radius: 8px !important;
    }

    /* Slider */
    .stSlider > div > div {
        color: #64ffda;
    }

    /* Esconder el menú de hamburguesa y footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    """Función principal del dashboard."""

    # ── Header ────────────────────────────────────
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <h1 style="color: #64ffda; font-size: 2.2rem; margin: 0;">
                🔄 Churn Intelligence Dashboard
            </h1>
            <p style="color: #8892b0; font-size: 1rem; margin-top: 5px;">
                Predicción de churn + Análisis de retención por cohortes — Olist E-commerce
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Cargar datos ──────────────────────────────
    try:
        predictions = cargar_predicciones()
        at_risk = cargar_at_risk()
        features = cargar_features()
        cohort_matrix = cargar_cohort_matrix()
        insights = cargar_insights()
        metrics = cargar_metricas()
        shap_values = cargar_shap_values()
    except Exception as e:
        st.error(
            f"❌ Error cargando datos: {e}\n\n"
            "Asegúrate de haber ejecutado el pipeline completo:\n"
            "```\n"
            "python pipeline/01_etl.py\n"
            "python pipeline/02_feature_engineering.py\n"
            "python pipeline/03_churn_model.py\n"
            "python pipeline/04_cohort_analysis.py\n"
            "python pipeline/05_insights_generator.py\n"
            "```"
        )
        st.stop()

    # ── Sidebar: Filtros ──────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <h3 style="color: #64ffda; margin: 0;">⚙️ Filtros</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Filtro de rango de fechas
        st.markdown("##### 📅 Rango de Fechas")
        fecha_min = predictions["first_purchase_date"].min().date()
        fecha_max = predictions["last_purchase_date"].max().date()

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fecha_inicio = st.date_input(
                "Desde",
                value=fecha_min,
                min_value=fecha_min,
                max_value=fecha_max,
                key="fecha_inicio",
            )
        with col_f2:
            fecha_fin = st.date_input(
                "Hasta",
                value=fecha_max,
                min_value=fecha_min,
                max_value=fecha_max,
                key="fecha_fin",
            )

        st.markdown("---")

        # Filtro de estado brasileño
        st.markdown("##### 🗺️ Estado")
        estados_disponibles = sorted(predictions["customer_state"].dropna().unique().tolist())
        estados_seleccionados = st.multiselect(
            "Selecciona estados",
            options=estados_disponibles,
            default=[],
            placeholder="Todos los estados",
            key="estados",
        )

        st.markdown("---")

        # Slider: umbral de riesgo
        st.markdown("##### 🎯 Umbral de Riesgo")
        umbral_riesgo = st.slider(
            "Probabilidad mínima para clasificar como 'en riesgo'",
            min_value=0.1,
            max_value=0.9,
            value=0.6,
            step=0.05,
            key="umbral",
        )

        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0;">
                <p style="color: #4a5568; font-size: 12px;">
                    🤖 Powered by XGBoost + SHAP<br>
                    📊 Dataset: Olist (2016-2018)
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Aplicar filtros ───────────────────────────
    predictions_filtrado = filtrar_datos(
        predictions,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estados=estados_seleccionados if estados_seleccionados else None,
    )

    features_filtrado = filtrar_datos(
        features,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estados=estados_seleccionados if estados_seleccionados else None,
    )

    # ── Tabs ──────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Overview",
        "📈 Cohort Retention",
        "🚨 Clientes en Riesgo",
        "🤖 Model Explainer",
        "🗺️ Geo Intelligence",
    ])

    # ── TAB 1: Executive Overview ─────────────────
    with tab1:
        st.markdown("## 📊 Executive Overview")
        st.markdown("---")

        # KPIs (recalcular con datos filtrados)
        kpis = insights.get("kpis", {})

        # Actualizar KPIs con datos filtrados si hay filtros activos
        if len(predictions_filtrado) < len(predictions):
            kpis_local = kpis.copy()
            kpis_local["total_clientes"] = len(predictions_filtrado)
            at_risk_filt = predictions_filtrado[predictions_filtrado["prob_churn"] > umbral_riesgo]
            kpis_local["clientes_en_riesgo_predicho"] = len(at_risk_filt)
            kpis_local["revenue_en_riesgo"] = round(float(at_risk_filt["total_revenue"].sum()), 2)
            if "churned" in predictions_filtrado.columns:
                kpis_local["churn_rate"] = round(predictions_filtrado["churned"].mean() * 100, 2)
                kpis_local["clientes_churned"] = int(predictions_filtrado["churned"].sum())
                kpis_local["clientes_activos"] = int((predictions_filtrado["churned"] == 0).sum())
            kpis_local["ltv_promedio"] = round(float(predictions_filtrado["total_revenue"].mean()), 2)
            kpis_local["avg_review_score"] = round(float(predictions_filtrado["avg_review_score"].mean()), 2)
            render_kpi_cards(kpis_local)
        else:
            render_kpi_cards(kpis)

        st.markdown("")

        # Gráficos
        col1, col2 = st.columns([3, 2])

        with col1:
            evolucion = insights.get("evolucion_churn_mensual", [])
            render_churn_trend(evolucion)

        with col2:
            churn_por_estado = insights.get("churn_por_estado", {})
            render_top_estados(churn_por_estado)

    # ── TAB 2: Cohort Retention ───────────────────
    with tab2:
        st.markdown("## 📈 Cohort Retention")
        st.markdown("---")

        # Comparativa cards
        render_cohort_comparison(insights)

        st.markdown("")

        # Heatmap
        render_cohort_heatmap(cohort_matrix)

        # Curvas de retención
        render_retention_curves(cohort_matrix)

    # ── TAB 3: At-Risk Customers ──────────────────
    with tab3:
        st.markdown("## 🚨 Clientes en Riesgo")
        st.markdown("---")

        # Filtrar at_risk con umbral del sidebar
        if "prob_churn" in predictions_filtrado.columns:
            at_risk_filtrado = predictions_filtrado[
                predictions_filtrado["prob_churn"] > umbral_riesgo
            ].sort_values("prob_churn", ascending=False)
        else:
            at_risk_filtrado = at_risk

        # Tabla y scatter en layout
        render_risk_table(at_risk_filtrado, umbral=umbral_riesgo)

        st.markdown("")

        render_risk_scatter(predictions_filtrado, umbral=umbral_riesgo)

    # ── TAB 4: Model Explainer ────────────────────
    with tab4:
        st.markdown("## 🤖 Model Explainer")
        st.markdown("---")

        # Métricas del modelo
        render_model_metrics(metrics)

        st.markdown("")

        # Layout: importancia global + explicación individual
        col_imp, col_shap = st.columns([1, 1])

        with col_imp:
            render_feature_importance(metrics)

        with col_shap:
            # Selector de cliente (de los de mayor riesgo)
            st.markdown("### 🔍 Explorar Cliente Individual")

            top_risk = predictions_filtrado.nlargest(50, "prob_churn")
            opciones_clientes = top_risk["customer_unique_id"].tolist()

            if opciones_clientes:
                selected_customer = st.selectbox(
                    "Selecciona un cliente (top 50 mayor riesgo)",
                    options=opciones_clientes,
                    format_func=lambda x: f"{x[:12]}... ({predictions_filtrado[predictions_filtrado['customer_unique_id'] == x]['prob_churn'].values[0]:.0%} riesgo)",
                    key="cliente_select",
                )

                # SHAP waterfall
                feature_cols = metrics.get("feature_importance", {}).keys()
                render_shap_waterfall(
                    shap_values,
                    predictions_filtrado,
                    list(feature_cols),
                    selected_customer,
                )

                # Explicación automática
                render_auto_explanation(predictions_filtrado, selected_customer)
            else:
                st.info("No hay clientes disponibles con los filtros actuales.")

    # ── TAB 5: Geo Intelligence ───────────────────
    with tab5:
        st.markdown("## 🗺️ Geo Intelligence")
        st.markdown("---")

        churn_por_estado = insights.get("churn_por_estado", {})
        render_churn_map(predictions_filtrado, churn_por_estado)

        st.markdown("")

        render_delivery_vs_churn(features_filtrado)


if __name__ == "__main__":
    main()
