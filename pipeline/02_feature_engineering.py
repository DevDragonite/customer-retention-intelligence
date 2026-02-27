"""
02_feature_engineering.py — Agente 2: Feature Engineering
=========================================================
Construye todas las features para el modelo de churn.

Definición de churn:
  - Churned (label=1): cliente que NO compró en los últimos 180 días
  - Activo  (label=0): cliente que SÍ compró en los últimos 180 días

Features:
  - Recencia: days_since_last/first_purchase, customer_tenure_days
  - Frecuencia: total_orders, avg_days_between_orders, orders_last_{30,60,90}d
  - Monetario (RFM): total_revenue, avg/max_order_value, revenue_trend
  - Satisfacción: avg/last review_score, pct_reviews_below_3, has_negative_review, trend
  - Logística: avg_delivery_days, delivery_delay_rate, avg_delay_days

Entrada:  data/processed/master_customers.parquet
Salida:   data/processed/churn_features.parquet
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd
import numpy as np
from scipy import stats

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
INPUT_FILE = PROCESSED_DIR / "master_customers.parquet"
OUTPUT_FILE = PROCESSED_DIR / "churn_features.parquet"

# Parámetro de churn: días sin compra para considerar churned
CHURN_DAYS = 180


def verificar_input() -> None:
    """Verifica que exista el archivo de entrada."""
    if not INPUT_FILE.exists():
        logger.error("❌ No se encontró: %s", INPUT_FILE)
        logger.error("   Ejecuta primero: python pipeline/01_etl.py")
        sys.exit(1)


def calcular_label_churn(df: pd.DataFrame, fecha_referencia: pd.Timestamp) -> pd.Series:
    """
    Calcula el label de churn basado en la regla de 180 días.

    Parameters
    ----------
    df : pd.DataFrame
        Tabla maestra con columna 'last_purchase_date'.
    fecha_referencia : pd.Timestamp
        Fecha de corte (máxima del dataset).

    Returns
    -------
    pd.Series
        1 = churned, 0 = activo.
    """
    dias_desde_ultima = (fecha_referencia - df["last_purchase_date"]).dt.days
    return (dias_desde_ultima > CHURN_DAYS).astype(int)


def calcular_tendencia(valores: list) -> float:
    """
    Calcula la pendiente de una regresión lineal simple sobre una lista de valores.
    Útil para revenue_trend y review_score_trend.

    Returns
    -------
    float
        Pendiente (slope). Positiva = creciente, negativa = decreciente.
    """
    # Limpiar valores nulos
    vals = [v for v in valores if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if len(vals) < 2:
        return 0.0
    x = np.arange(len(vals))
    slope, _, _, _, _ = stats.linregress(x, vals)
    return round(slope, 4)


def contar_ordenes_ultimos_n_dias(
    order_dates: list, fecha_referencia: pd.Timestamp, n_dias: int
) -> int:
    """Cuenta cuántas órdenes hubo en los últimos N días antes de la fecha de referencia."""
    fecha_limite = fecha_referencia - pd.Timedelta(days=n_dias)
    return sum(
        1 for d in order_dates
        if d is not None and pd.notna(d) and pd.Timestamp(d) >= fecha_limite
    )


def construir_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye todas las features a partir de la tabla maestra.

    Parameters
    ----------
    df : pd.DataFrame
        Tabla maestra de clientes (output del ETL).

    Returns
    -------
    pd.DataFrame
        DataFrame con todas las features y el label de churn.
    """
    fecha_referencia = df["last_purchase_date"].max()
    logger.info("📅 Fecha de referencia (máxima del dataset): %s",
                fecha_referencia.strftime("%Y-%m-%d"))

    # ── Label de churn ───────────────────────────
    df["churned"] = calcular_label_churn(df, fecha_referencia)
    tasa_churn = df["churned"].mean()
    logger.info("🏷️  Label churn calculado: %.1f%% churned, %.1f%% activos",
                tasa_churn * 100, (1 - tasa_churn) * 100)

    # ── FEATURES DE RECENCIA ─────────────────────
    logger.info("⏰ Calculando features de recencia ...")
    df["days_since_last_purchase"] = (
        fecha_referencia - df["last_purchase_date"]
    ).dt.days

    df["days_since_first_purchase"] = (
        fecha_referencia - df["first_purchase_date"]
    ).dt.days

    df["customer_tenure_days"] = (
        df["last_purchase_date"] - df["first_purchase_date"]
    ).dt.days

    # ── FEATURES DE FRECUENCIA ───────────────────
    logger.info("🔄 Calculando features de frecuencia ...")

    # avg_days_between_orders: promedio de días entre compras sucesivas
    def _avg_days_between(dates_list: list) -> float:
        """Calcula promedio de días entre compras consecutivas."""
        dates = sorted([pd.Timestamp(d) for d in dates_list if d is not None and pd.notna(d)])
        if len(dates) < 2:
            return 0.0
        diffs = [(dates[i + 1] - dates[i]).total_seconds() / 86400 for i in range(len(dates) - 1)]
        return round(np.mean(diffs), 1)

    df["avg_days_between_orders"] = df["order_dates"].apply(_avg_days_between)

    # Órdenes en los últimos 30, 60, 90 días
    df["orders_last_30d"] = df["order_dates"].apply(
        lambda dates: contar_ordenes_ultimos_n_dias(dates, fecha_referencia, 30)
    )
    df["orders_last_60d"] = df["order_dates"].apply(
        lambda dates: contar_ordenes_ultimos_n_dias(dates, fecha_referencia, 60)
    )
    df["orders_last_90d"] = df["order_dates"].apply(
        lambda dates: contar_ordenes_ultimos_n_dias(dates, fecha_referencia, 90)
    )

    # ── FEATURES MONETARIOS (RFM) ────────────────
    logger.info("💰 Calculando features monetarios ...")

    df["avg_order_value"] = df.apply(
        lambda row: round(row["total_revenue"] / row["total_orders"], 2)
        if row["total_orders"] > 0 else 0.0,
        axis=1,
    )

    def _max_order_value(vals) -> float:
        """Máximo valor de orden, maneja arrays numpy y listas."""
        try:
            arr = np.array(vals, dtype=float)
            valid = arr[~np.isnan(arr)]
            return round(float(valid.max()), 2) if len(valid) > 0 else 0.0
        except (ValueError, TypeError):
            return 0.0

    df["max_order_value"] = df["order_revenues"].apply(_max_order_value)

    # Tendencia de revenue (pendiente de regresión sobre los montos)
    def _safe_trend(vals) -> float:
        """Calcula tendencia manejando arrays numpy."""
        arr = np.array(vals, dtype=float)
        valid = arr[~np.isnan(arr)]
        if len(valid) < 2:
            return 0.0
        x = np.arange(len(valid))
        slope, _, _, _, _ = stats.linregress(x, valid)
        return round(slope, 4)

    df["revenue_trend"] = df["order_revenues"].apply(_safe_trend)

    # ── FEATURES DE SATISFACCIÓN ─────────────────
    logger.info("⭐ Calculando features de satisfacción ...")

    # Último review score
    def _last_review(vals) -> float:
        """Obtiene el último review score válido."""
        arr = np.array(vals, dtype=float)
        valid = arr[~np.isnan(arr)]
        return float(valid[-1]) if len(valid) > 0 else np.nan

    df["last_review_score"] = df["review_scores"].apply(_last_review)

    # Porcentaje de reviews por debajo de 3
    def _pct_below_3(scores) -> float:
        """Porcentaje de reviews con score < 3."""
        arr = np.array(scores, dtype=float)
        valid = arr[~np.isnan(arr)]
        if len(valid) == 0:
            return 0.0
        return round(float(np.sum(valid < 3)) / len(valid), 4)

    df["pct_reviews_below_3"] = df["review_scores"].apply(_pct_below_3)

    # Flag: ¿tiene al menos un review negativo (score ≤ 2)?
    def _has_negative(vals) -> int:
        """Flag binario: tiene al menos un review ≤ 2."""
        arr = np.array(vals, dtype=float)
        valid = arr[~np.isnan(arr)]
        return int(np.any(valid <= 2)) if len(valid) > 0 else 0

    df["has_negative_review"] = df["review_scores"].apply(_has_negative)

    # Tendencia del review score
    df["review_score_trend"] = df["review_scores"].apply(_safe_trend)

    # ── FEATURES LOGÍSTICOS ──────────────────────
    logger.info("🚚 Calculando features logísticos ...")

    # Tasa de entregas tardías
    def _delay_rate(vals) -> float:
        """Tasa de entregas tardías, maneja arrays numpy."""
        arr = np.array(vals, dtype=float)
        valid = arr[~np.isnan(arr)]
        return round(float(np.mean(valid)), 4) if len(valid) > 0 else 0.0

    df["delivery_delay_rate"] = df["is_late_list"].apply(_delay_rate)

    # Promedio de días de retraso (solo entregas tardías)
    def _avg_delay(delays) -> float:
        """Promedio de días de retraso (solo positivos)."""
        arr = np.array(delays, dtype=float)
        valid = arr[~np.isnan(arr)]
        positivos = valid[valid > 0]
        return round(float(np.mean(positivos)), 1) if len(positivos) > 0 else 0.0

    df["avg_delay_days"] = df["delivery_delay_list"].apply(_avg_delay)

    return df


def seleccionar_columnas_finales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona solo las columnas necesarias para el modelo,
    eliminando las listas auxiliares del ETL.
    """
    columnas = [
        # Identificador
        "customer_unique_id",
        # Fechas (para split temporal)
        "first_purchase_date",
        "last_purchase_date",
        # Metadata
        "customer_state",
        # Label
        "churned",
        # Recencia
        "days_since_last_purchase",
        "days_since_first_purchase",
        "customer_tenure_days",
        # Frecuencia
        "total_orders",
        "avg_days_between_orders",
        "orders_last_30d",
        "orders_last_60d",
        "orders_last_90d",
        # Monetario
        "total_revenue",
        "avg_order_value",
        "max_order_value",
        "revenue_trend",
        # Satisfacción
        "avg_review_score",
        "last_review_score",
        "pct_reviews_below_3",
        "has_negative_review",
        "review_score_trend",
        # Logística
        "avg_delivery_days",
        "delivery_delay_rate",
        "avg_delay_days",
    ]
    return df[columnas].copy()


def main() -> None:
    """Punto de entrada principal del Feature Engineering."""
    logger.info("=" * 60)
    logger.info("AGENTE 2 — Feature Engineering para Churn Prediction")
    logger.info("=" * 60)

    # Verificar input
    verificar_input()

    # Cargar tabla maestra
    logger.info("📂 Cargando %s ...", INPUT_FILE.name)
    df = pd.read_parquet(INPUT_FILE)
    logger.info("   → %d clientes cargados", len(df))

    # Convertir fechas (por si se serializaron como string)
    df["first_purchase_date"] = pd.to_datetime(df["first_purchase_date"])
    df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])

    # Construir features
    df = construir_features(df)

    # Seleccionar columnas finales
    df_final = seleccionar_columnas_finales(df)

    # Rellenar NaN en features numéricas con la mediana
    cols_numericas = df_final.select_dtypes(include=[np.number]).columns
    for col in cols_numericas:
        n_nulos = df_final[col].isna().sum()
        if n_nulos > 0:
            mediana = df_final[col].median()
            df_final[col] = df_final[col].fillna(mediana)
            logger.info("   ⚠️  %s: %d NaN rellenados con mediana (%.2f)", col, n_nulos, mediana)

    # Guardar resultado
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(OUTPUT_FILE, index=False, engine="pyarrow")
    tamaño_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    logger.info("💾 Guardado en %s (%.1f MB)", OUTPUT_FILE, tamaño_mb)

    # Resumen de features
    logger.info("\n📊 Resumen de features:")
    logger.info("   Total clientes: %d", len(df_final))
    logger.info("   Churned: %d (%.1f%%)",
                df_final["churned"].sum(),
                df_final["churned"].mean() * 100)
    logger.info("   Features numéricas: %d", len(cols_numericas))
    logger.info("   Columnas totales: %d", len(df_final.columns))

    logger.info("=" * 60)
    logger.info("✅ Feature Engineering completado exitosamente")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
