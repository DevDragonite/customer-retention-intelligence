"""
04_cohort_analysis.py — Agente 4: Análisis de Cohortes
======================================================
Construye la matriz de retención por cohortes mensuales.

Lógica:
  - Cohort = mes de la primera compra de cada cliente
  - Para cada compra posterior, period_number = meses transcurridos
  - Retención = % de clientes del cohort original que vuelven a comprar

Entrada:  data/processed/master_customers.parquet
Salidas:
  - data/processed/cohort_matrix.parquet
  - data/processed/revenue_cohort_matrix.parquet
  - data/outputs/cohort_insights.json
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"
INPUT_FILE = PROCESSED_DIR / "master_customers.parquet"


def verificar_input() -> None:
    """Verifica que exista el archivo de entrada."""
    if not INPUT_FILE.exists():
        logger.error("❌ No se encontró: %s", INPUT_FILE)
        logger.error("   Ejecuta primero: python pipeline/01_etl.py")
        sys.exit(1)


def expandir_ordenes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande la tabla maestra a una fila por orden por cliente.
    Usa explode() para velocidad en lugar de iterrows().

    Returns
    -------
    pd.DataFrame con columnas: customer_unique_id, order_date, order_revenue
    """
    logger.info("📊 Expandiendo órdenes por cliente ...")

    # Seleccionar solo las columnas necesarias
    expand_df = df[["customer_unique_id", "order_dates", "order_revenues"]].copy()

    # Explode las fechas
    expand_dates = expand_df[["customer_unique_id", "order_dates"]].explode("order_dates")
    expand_dates = expand_dates.rename(columns={"order_dates": "order_date"})
    expand_dates = expand_dates.reset_index(drop=True)

    # Explode los revenues
    expand_rev = expand_df[["customer_unique_id", "order_revenues"]].explode("order_revenues")
    expand_rev = expand_rev.rename(columns={"order_revenues": "order_revenue"})
    expand_rev = expand_rev.reset_index(drop=True)

    # Combinar
    orders_df = pd.DataFrame({
        "customer_unique_id": expand_dates["customer_unique_id"],
        "order_date": pd.to_datetime(expand_dates["order_date"], errors="coerce"),
        "order_revenue": pd.to_numeric(expand_rev["order_revenue"], errors="coerce").fillna(0),
    })

    # Eliminar filas con fecha nula
    orders_df = orders_df.dropna(subset=["order_date"]).reset_index(drop=True)

    logger.info("   → %d órdenes de %d clientes",
                len(orders_df), orders_df["customer_unique_id"].nunique())
    return orders_df


def calcular_cohorts(orders_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calcula matrices de retención por cohortes (clientes y revenue).

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (customer_retention_matrix, revenue_retention_matrix)
    """
    # Cohort = mes de primera compra
    first_purchase = (
        orders_df.groupby("customer_unique_id")["order_date"]
        .min()
        .reset_index()
        .rename(columns={"order_date": "first_order_date"})
    )
    first_purchase["cohort_month"] = first_purchase["first_order_date"].dt.to_period("M")

    # Unir cohort con cada orden
    orders_df = orders_df.merge(
        first_purchase[["customer_unique_id", "cohort_month"]],
        on="customer_unique_id",
        how="left",
    )

    # period_number = meses entre la orden y el cohort
    orders_df["order_month"] = orders_df["order_date"].dt.to_period("M")
    orders_df["period_number"] = (
        orders_df["order_month"].astype(int) - orders_df["cohort_month"].astype(int)
    )

    # ── Retención de clientes ────────────────────
    logger.info("📊 Construyendo matriz de retención de clientes ...")

    cohort_sizes = (
        orders_df[orders_df["period_number"] == 0]
        .groupby("cohort_month")["customer_unique_id"]
        .nunique()
        .rename("cohort_size")
    )

    active_customers = (
        orders_df.groupby(["cohort_month", "period_number"])["customer_unique_id"]
        .nunique()
        .reset_index()
        .rename(columns={"customer_unique_id": "n_customers"})
    )

    customer_matrix = active_customers.pivot_table(
        index="cohort_month", columns="period_number",
        values="n_customers", fill_value=0,
    )

    customer_retention = customer_matrix.divide(cohort_sizes, axis=0) * 100
    customer_retention = customer_retention.round(2)

    # ── Retención de revenue ─────────────────────
    logger.info("📊 Construyendo matriz de retención de revenue ...")

    revenue_m0 = (
        orders_df[orders_df["period_number"] == 0]
        .groupby("cohort_month")["order_revenue"]
        .sum()
        .rename("revenue_m0")
    )

    revenue_by_period = (
        orders_df.groupby(["cohort_month", "period_number"])["order_revenue"]
        .sum()
        .reset_index()
    )

    revenue_matrix = revenue_by_period.pivot_table(
        index="cohort_month", columns="period_number",
        values="order_revenue", fill_value=0,
    )

    revenue_retention = revenue_matrix.divide(revenue_m0, axis=0) * 100
    revenue_retention = revenue_retention.round(2)

    logger.info("   → %d cohortes, hasta M+%d períodos",
                len(customer_retention),
                int(customer_retention.columns.max()) if len(customer_retention.columns) > 0 else 0)

    return customer_retention, revenue_retention


def generar_insights(
    customer_ret: pd.DataFrame,
    revenue_ret: pd.DataFrame,
) -> Dict[str, Any]:
    """Genera insights clave de los cohortes."""
    insights: Dict[str, Any] = {}

    # Mejor y peor cohort en M+3
    if 3 in customer_ret.columns:
        ret_m3 = customer_ret[3].dropna()
        if len(ret_m3) > 0:
            insights["mejor_cohort_m3"] = {
                "cohort": str(ret_m3.idxmax()),
                "retencion_pct": round(float(ret_m3.max()), 2),
            }
            insights["peor_cohort_m3"] = {
                "cohort": str(ret_m3.idxmin()),
                "retencion_pct": round(float(ret_m3.min()), 2),
            }
            logger.info("🏆 Mejor cohort M+3: %s (%.1f%%)", str(ret_m3.idxmax()), ret_m3.max())
            logger.info("📉 Peor cohort M+3: %s (%.1f%%)", str(ret_m3.idxmin()), ret_m3.min())

    # Churn cliff
    avg_retention = customer_ret.mean(axis=0).sort_index()
    drops = avg_retention.diff().dropna()
    if len(drops) > 0:
        worst_period = int(drops.idxmin())
        worst_drop = round(float(drops.min()), 2)
        insights["churn_cliff"] = {
            "periodo": f"M+{worst_period - 1} → M+{worst_period}",
            "drop_pct": worst_drop,
            "descripcion": f"Mayor caída de retención entre M+{worst_period - 1} y M+{worst_period} ({worst_drop}%)",
        }
        logger.info("🪨 Churn cliff: M+%d → M+%d (drop: %.1f%%)",
                    worst_period - 1, worst_period, worst_drop)

    # Retención promedio por período
    insights["retencion_promedio_por_periodo"] = {
        f"M+{int(k)}": round(float(v), 2)
        for k, v in avg_retention.items() if int(k) <= 12
    }

    insights["total_cohortes"] = len(customer_ret)
    insights["periodos_maximos"] = int(customer_ret.columns.max()) if len(customer_ret.columns) > 0 else 0

    if 1 in customer_ret.columns:
        insights["retencion_promedio_m1"] = round(float(customer_ret[1].mean()), 2)
        logger.info("📊 Retención promedio M+1: %.1f%%", customer_ret[1].mean())

    return insights


def main() -> None:
    """Punto de entrada principal."""
    logger.info("=" * 60)
    logger.info("AGENTE 4 — Análisis de Cohortes de Retención")
    logger.info("=" * 60)

    verificar_input()

    # Cargar tabla maestra
    logger.info("📂 Cargando %s ...", INPUT_FILE.name)
    df = pd.read_parquet(INPUT_FILE)
    logger.info("   → %d clientes", len(df))

    # Expandir órdenes
    orders_df = expandir_ordenes(df)

    if orders_df.empty:
        logger.error("❌ No se pudieron expandir órdenes. Verificar formato de datos.")
        sys.exit(1)

    # Calcular matrices
    customer_ret, revenue_ret = calcular_cohorts(orders_df)

    # Generar insights
    insights = generar_insights(customer_ret, revenue_ret)

    # Guardar
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Convertir Period index a string para parquet
    for matrix, name, path in [
        (customer_ret, "clientes", PROCESSED_DIR / "cohort_matrix.parquet"),
        (revenue_ret, "revenue", PROCESSED_DIR / "revenue_cohort_matrix.parquet"),
    ]:
        save_df = matrix.copy()
        save_df.index = save_df.index.astype(str)
        save_df.columns = [f"M+{c}" for c in save_df.columns]
        save_df.index.name = "cohort_month"
        save_df.reset_index().to_parquet(path, index=False, engine="pyarrow")
        logger.info("💾 Matriz de cohortes (%s) guardada en %s", name, path)

    # Insights JSON
    insights_path = OUTPUTS_DIR / "cohort_insights.json"
    with open(insights_path, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
    logger.info("💾 Insights guardados en %s", insights_path)

    logger.info("=" * 60)
    logger.info("✅ Análisis de cohortes completado exitosamente")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
