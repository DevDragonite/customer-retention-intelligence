"""
05_insights_generator.py — Agente 5: Generador de Insights
===========================================================
Agrega insights de negocio de alto nivel para consumo del dashboard.

Entrada:
  - data/processed/churn_features.parquet
  - data/outputs/churn_predictions.csv
  - data/outputs/metrics_report.json
  - data/outputs/cohort_insights.json

Salida:
  - data/outputs/dashboard_insights.json
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Configuración de logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Rutas del proyecto
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"

# Archivos de entrada
FEATURES_FILE = PROCESSED_DIR / "churn_features.parquet"
PREDICTIONS_FILE = OUTPUTS_DIR / "churn_predictions.csv"
METRICS_FILE = OUTPUTS_DIR / "metrics_report.json"
COHORT_INSIGHTS_FILE = OUTPUTS_DIR / "cohort_insights.json"


def verificar_inputs() -> None:
    """Verifica que existan todos los archivos necesarios."""
    archivos = {
        "churn_features.parquet": FEATURES_FILE,
        "churn_predictions.csv": PREDICTIONS_FILE,
        "metrics_report.json": METRICS_FILE,
        "cohort_insights.json": COHORT_INSIGHTS_FILE,
    }
    faltantes = {n: p for n, p in archivos.items() if not p.exists()}
    if faltantes:
        logger.error("❌ Faltan los siguientes archivos:")
        for nombre, ruta in faltantes.items():
            logger.error("   - %s → %s", nombre, ruta)
        logger.error("   Ejecuta los scripts anteriores primero (01 al 04)")
        sys.exit(1)
    logger.info("✅ Todos los archivos de entrada verificados")


def calcular_ltv_promedio(df: pd.DataFrame) -> float:
    """
    Calcula el Customer Lifetime Value (LTV) promedio simplificado.
    LTV = total_revenue promedio por cliente.
    """
    return round(float(df["total_revenue"].mean()), 2)


def calcular_kpis(
    features_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calcula los KPIs principales para el dashboard.

    Returns
    -------
    Dict con KPIs de negocio.
    """
    kpis = {}

    # Total de clientes
    kpis["total_clientes"] = len(features_df)

    # Churn rate actual (basado en definición de 180 días)
    churn_rate = features_df["churned"].mean()
    kpis["churn_rate"] = round(churn_rate * 100, 2)
    kpis["clientes_churned"] = int(features_df["churned"].sum())
    kpis["clientes_activos"] = int((features_df["churned"] == 0).sum())

    # Revenue en riesgo (clientes predichos como churn × su revenue)
    at_risk = predictions_df[predictions_df["pred_churn"] == 1]
    kpis["revenue_en_riesgo"] = round(float(at_risk["total_revenue"].sum()), 2)
    kpis["clientes_en_riesgo_predicho"] = len(at_risk)

    # LTV promedio
    kpis["ltv_promedio"] = calcular_ltv_promedio(features_df)

    # Revenue total
    kpis["revenue_total"] = round(float(features_df["total_revenue"].sum()), 2)

    # Días promedio desde última compra
    kpis["avg_days_since_last_purchase"] = round(
        float(features_df["days_since_last_purchase"].mean()), 1
    )

    # Review score promedio
    kpis["avg_review_score"] = round(
        float(features_df["avg_review_score"].mean()), 2
    )

    return kpis


def calcular_churn_por_estado(predictions_df: pd.DataFrame) -> Dict[str, float]:
    """Calcula la tasa de churn por estado brasileño."""
    churn_por_estado = (
        predictions_df.groupby("customer_state")
        .agg(
            total=("customer_unique_id", "count"),
            churned=("pred_churn", "sum"),
        )
        .assign(churn_rate=lambda x: round(x["churned"] / x["total"] * 100, 2))
        .sort_values("churn_rate", ascending=False)
    )
    return {
        estado: {
            "total": int(row["total"]),
            "churned": int(row["churned"]),
            "churn_rate": float(row["churn_rate"]),
        }
        for estado, row in churn_por_estado.iterrows()
    }


def calcular_evolucion_churn(features_df: pd.DataFrame) -> list:
    """
    Calcula la evolución mensual del churn rate.
    Agrupa clientes por su mes de última compra y calcula la proporción de churned.
    """
    df = features_df.copy()
    df["last_purchase_month"] = pd.to_datetime(df["last_purchase_date"]).dt.to_period("M")

    evolucion = (
        df.groupby("last_purchase_month")
        .agg(
            total=("customer_unique_id", "count"),
            churned=("churned", "sum"),
        )
        .assign(churn_rate=lambda x: round(x["churned"] / x["total"] * 100, 2))
        .reset_index()
    )

    return [
        {
            "mes": str(row["last_purchase_month"]),
            "total_clientes": int(row["total"]),
            "churned": int(row["churned"]),
            "churn_rate": float(row["churn_rate"]),
        }
        for _, row in evolucion.iterrows()
    ]


def main() -> None:
    """Punto de entrada principal del generador de insights."""
    logger.info("=" * 60)
    logger.info("AGENTE 5 — Generador de Insights para Dashboard")
    logger.info("=" * 60)

    # Verificar inputs
    verificar_inputs()

    # Cargar datos
    logger.info("📂 Cargando datos ...")
    features_df = pd.read_parquet(FEATURES_FILE)
    predictions_df = pd.read_csv(PREDICTIONS_FILE)

    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(COHORT_INSIGHTS_FILE, "r", encoding="utf-8") as f:
        cohort_insights = json.load(f)

    logger.info("   → Features: %d clientes", len(features_df))
    logger.info("   → Predicciones: %d clientes", len(predictions_df))

    # Calcular insights
    logger.info("📊 Calculando KPIs ...")
    kpis = calcular_kpis(features_df, predictions_df)

    logger.info("📊 Calculando churn por estado ...")
    churn_por_estado = calcular_churn_por_estado(predictions_df)

    logger.info("📊 Calculando evolución mensual del churn ...")
    evolucion_churn = calcular_evolucion_churn(features_df)

    # Compilar insights finales
    dashboard_insights = {
        "kpis": kpis,
        "churn_por_estado": churn_por_estado,
        "evolucion_churn_mensual": evolucion_churn,
        "modelo": {
            "nombre": metrics.get("mejor_modelo", "N/A"),
            "threshold": metrics.get("threshold_optimo", 0.5),
            "metricas_test": metrics.get("resultados_test", {}),
            "feature_importance": metrics.get("feature_importance", {}),
        },
        "cohort_insights": cohort_insights,
    }

    # Guardar
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUTS_DIR / "dashboard_insights.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_insights, f, indent=2, ensure_ascii=False, default=str)
    logger.info("💾 Insights guardados en %s", output_path)

    # Resumen
    logger.info("\n📋 Resumen de KPIs:")
    logger.info("   Total clientes: %d", kpis["total_clientes"])
    logger.info("   Churn rate: %.1f%%", kpis["churn_rate"])
    logger.info("   Revenue en riesgo: R$ {:,.2f}".format(kpis["revenue_en_riesgo"]))
    logger.info("   LTV promedio: R$ {:,.2f}".format(kpis["ltv_promedio"]))
    logger.info("   Estados analizados: %d", len(churn_por_estado))

    logger.info("=" * 60)
    logger.info("✅ Generación de insights completada exitosamente")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
