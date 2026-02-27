"""
utils.py — Utilidades de carga de datos para el Dashboard
=========================================================
Funciones centralizadas de carga con st.cache_data para rendimiento.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────
# Rutas del proyecto
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"


@st.cache_data(ttl=3600)
def cargar_predicciones() -> pd.DataFrame:
    """Carga las predicciones de churn."""
    path = OUTPUTS_DIR / "churn_predictions.csv"
    if not path.exists():
        st.error(f"❌ No se encontró: {path}\nEjecuta primero el pipeline completo.")
        st.stop()
    df = pd.read_csv(path)
    df["first_purchase_date"] = pd.to_datetime(df["first_purchase_date"])
    df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])
    return df


@st.cache_data(ttl=3600)
def cargar_at_risk() -> pd.DataFrame:
    """Carga los clientes en riesgo."""
    path = OUTPUTS_DIR / "at_risk_customers.csv"
    if not path.exists():
        st.error(f"❌ No se encontró: {path}\nEjecuta primero el pipeline completo.")
        st.stop()
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def cargar_features() -> pd.DataFrame:
    """Carga las features de churn."""
    path = PROCESSED_DIR / "churn_features.parquet"
    if not path.exists():
        st.error(f"❌ No se encontró: {path}\nEjecuta primero el pipeline completo.")
        st.stop()
    df = pd.read_parquet(path)
    df["first_purchase_date"] = pd.to_datetime(df["first_purchase_date"])
    df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])
    return df


@st.cache_data(ttl=3600)
def cargar_cohort_matrix() -> pd.DataFrame:
    """Carga la matriz de cohortes de clientes."""
    path = PROCESSED_DIR / "cohort_matrix.parquet"
    if not path.exists():
        st.error(f"❌ No se encontró: {path}\nEjecuta primero el pipeline completo.")
        st.stop()
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def cargar_revenue_cohort_matrix() -> pd.DataFrame:
    """Carga la matriz de cohortes de revenue."""
    path = PROCESSED_DIR / "revenue_cohort_matrix.parquet"
    if not path.exists():
        return pd.DataFrame()  # Puede no existir, no es crítico
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def cargar_insights() -> Dict[str, Any]:
    """Carga los insights del dashboard."""
    path = OUTPUTS_DIR / "dashboard_insights.json"
    if not path.exists():
        st.error(f"❌ No se encontró: {path}\nEjecuta primero el pipeline completo.")
        st.stop()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def cargar_metricas() -> Dict[str, Any]:
    """Carga el reporte de métricas del modelo."""
    path = OUTPUTS_DIR / "metrics_report.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def cargar_shap_values() -> Optional[pd.DataFrame]:
    """Carga los SHAP values si existen."""
    path = OUTPUTS_DIR / "shap_values.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


def filtrar_datos(
    df: pd.DataFrame,
    fecha_inicio: Optional[pd.Timestamp] = None,
    fecha_fin: Optional[pd.Timestamp] = None,
    estados: Optional[list] = None,
    umbral_riesgo: float = 0.6,
) -> pd.DataFrame:
    """
    Aplica filtros de sidebar al DataFrame de predicciones.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con predicciones.
    fecha_inicio : pd.Timestamp, optional
        Fecha mínima de primera compra.
    fecha_fin : pd.Timestamp, optional
        Fecha máxima de última compra.
    estados : list, optional
        Lista de estados brasileños a incluir.
    umbral_riesgo : float
        No se aplica como filtro global, sino que se pasa a componentes específicos.

    Returns
    -------
    pd.DataFrame filtrado.
    """
    mask = pd.Series(True, index=df.index)

    if fecha_inicio is not None:
        mask &= df["first_purchase_date"] >= pd.to_datetime(fecha_inicio)

    if fecha_fin is not None:
        mask &= df["last_purchase_date"] <= pd.to_datetime(fecha_fin)

    if estados and len(estados) > 0:
        mask &= df["customer_state"].isin(estados)

    return df[mask].copy()
