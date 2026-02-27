"""
01_etl.py — Agente 1: ETL
=========================
Une los 9 CSVs de Olist en una tabla maestra por customer_unique_id.
Solo procesa órdenes con status = 'delivered'.

Entrada:  data/raw/*.csv (9 archivos)
Salida:   data/processed/master_customers.parquet
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Configuración de logging
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Rutas del proyecto
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
LOG_DIR = PROJECT_ROOT / "data" / "outputs" / "logs"

# Archivos de entrada requeridos
REQUIRED_FILES = [
    "olist_orders_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]


def verificar_archivos_entrada() -> None:
    """Verifica que todos los archivos CSV requeridos existan en data/raw/."""
    faltantes = [f for f in REQUIRED_FILES if not (RAW_DIR / f).exists()]
    if faltantes:
        logger.error(
            "Faltan los siguientes archivos en %s:\n  - %s",
            RAW_DIR,
            "\n  - ".join(faltantes),
        )
        logger.error(
            "Descarga el dataset de Olist desde Kaggle y coloca los CSVs en data/raw/"
        )
        sys.exit(1)
    logger.info("✅ Todos los archivos de entrada encontrados (%d archivos)", len(REQUIRED_FILES))


def cargar_csv(nombre: str, **kwargs) -> pd.DataFrame:
    """Carga un CSV desde data/raw/ con logging."""
    ruta = RAW_DIR / nombre
    logger.info("📂 Cargando %s ...", nombre)
    df = pd.read_csv(ruta, **kwargs)
    logger.info("   → %d filas, %d columnas", len(df), len(df.columns))
    return df


def ejecutar_etl() -> pd.DataFrame:
    """
    Pipeline ETL completo:
    1. Carga los 9 CSVs
    2. Filtra órdenes entregadas
    3. Une tablas por order_id y customer_id
    4. Agrega métricas por customer_unique_id
    5. Retorna tabla maestra de clientes

    Returns
    -------
    pd.DataFrame
        Tabla maestra con una fila por customer_unique_id.
    """
    # ── 1. Cargar datos ──────────────────────────
    orders = cargar_csv("olist_orders_dataset.csv")
    customers = cargar_csv("olist_customers_dataset.csv")
    items = cargar_csv("olist_order_items_dataset.csv")
    payments = cargar_csv("olist_order_payments_dataset.csv")
    reviews = cargar_csv("olist_order_reviews_dataset.csv")
    products = cargar_csv("olist_products_dataset.csv")
    sellers = cargar_csv("olist_sellers_dataset.csv")
    # geolocation no se une directamente, se usa la info de estado del cliente
    # translation se usa para enriquecer categorías de producto
    translation = cargar_csv("product_category_name_translation.csv")

    # ── 2. Filtrar solo órdenes entregadas ───────
    total_ordenes = len(orders)
    orders = orders[orders["order_status"] == "delivered"].copy()
    logger.info(
        "🔍 Órdenes entregadas: %d / %d (%.1f%%)",
        len(orders),
        total_ordenes,
        100 * len(orders) / total_ordenes,
    )

    # ── 3. Convertir columnas de fecha ───────────
    cols_fecha = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in cols_fecha:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    # ── 4. Unir orders ↔ customers ───────────────
    # IMPORTANTE: usamos customer_unique_id, NO customer_id
    orders = orders.merge(
        customers[["customer_id", "customer_unique_id", "customer_state"]],
        on="customer_id",
        how="left",
    )
    logger.info("🔗 Orders + Customers unidos: %d filas", len(orders))

    # ── 5. Calcular revenue por orden ────────────
    # Sumamos payment_value por order_id (puede haber múltiples pagos)
    revenue_por_orden = (
        payments.groupby("order_id")["payment_value"]
        .sum()
        .reset_index()
        .rename(columns={"payment_value": "order_revenue"})
    )
    orders = orders.merge(revenue_por_orden, on="order_id", how="left")
    orders["order_revenue"] = orders["order_revenue"].fillna(0)

    # ── 6. Calcular review score por orden ───────
    # Si hay múltiples reviews por orden, tomamos el promedio
    review_por_orden = (
        reviews.groupby("order_id")["review_score"]
        .mean()
        .reset_index()
        .rename(columns={"review_score": "order_review_score"})
    )
    orders = orders.merge(review_por_orden, on="order_id", how="left")

    # ── 7. Calcular días de entrega ──────────────
    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400  # convertir a días

    # Días de retraso = entrega real - estimada (positivo = tarde)
    orders["delivery_delay_days"] = (
        orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    orders["is_late"] = (orders["delivery_delay_days"] > 0).astype(int)

    # ── 8. Agregar por customer_unique_id ────────
    logger.info("📊 Agregando métricas por customer_unique_id ...")

    master = orders.groupby("customer_unique_id").agg(
        first_purchase_date=("order_purchase_timestamp", "min"),
        last_purchase_date=("order_purchase_timestamp", "max"),
        total_orders=("order_id", "nunique"),
        total_revenue=("order_revenue", "sum"),
        avg_review_score=("order_review_score", "mean"),
        avg_delivery_days=("delivery_days", "mean"),
        customer_state=("customer_state", "first"),  # estado más frecuente
        # Columnas auxiliares para feature engineering posterior
        order_dates=("order_purchase_timestamp", list),
        order_revenues=("order_revenue", list),
        review_scores=("order_review_score", list),
        delivery_days_list=("delivery_days", list),
        delivery_delay_list=("delivery_delay_days", list),
        is_late_list=("is_late", list),
    ).reset_index()

    # ── 9. Redondear valores ─────────────────────
    master["total_revenue"] = master["total_revenue"].round(2)
    master["avg_review_score"] = master["avg_review_score"].round(2)
    master["avg_delivery_days"] = master["avg_delivery_days"].round(1)

    logger.info("✅ Tabla maestra generada: %d clientes únicos", len(master))
    logger.info("   Rango de fechas: %s → %s",
                master["first_purchase_date"].min().strftime("%Y-%m-%d"),
                master["last_purchase_date"].max().strftime("%Y-%m-%d"))
    logger.info("   Revenue total: R$ {:,.2f}".format(master["total_revenue"].sum()))

    return master


def guardar_parquet(df: pd.DataFrame, ruta: Path) -> None:
    """Guarda un DataFrame como parquet, creando directorios si es necesario."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ruta, index=False, engine="pyarrow")
    tamaño_mb = ruta.stat().st_size / (1024 * 1024)
    logger.info("💾 Guardado en %s (%.1f MB)", ruta, tamaño_mb)


def main() -> None:
    """Punto de entrada principal del ETL."""
    logger.info("=" * 60)
    logger.info("AGENTE 1 — ETL: Construcción de tabla maestra de clientes")
    logger.info("=" * 60)

    # Verificar que existan los archivos de entrada
    verificar_archivos_entrada()

    # Ejecutar ETL
    master = ejecutar_etl()

    # Guardar resultado
    output_path = PROCESSED_DIR / "master_customers.parquet"
    guardar_parquet(master, output_path)

    logger.info("=" * 60)
    logger.info("✅ ETL completado exitosamente")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
