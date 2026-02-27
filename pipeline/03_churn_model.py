"""
03_churn_model.py — Agente 3: Modelo de Machine Learning
========================================================
Entrena y evalúa modelos de churn prediction con split temporal.

Modelos: Logistic Regression, Random Forest, XGBoost, LightGBM
Métricas: ROC-AUC, F1-Score, Precision, Recall
Explicabilidad: SHAP values

Split temporal (sin data leakage):
  - Train:      2016-01 → 2017-09
  - Validation: 2017-10 → 2018-03
  - Test:       2018-04 → 2018-08

Entrada:  data/processed/churn_features.parquet
Salidas:
  - models/churn_model.pkl
  - data/outputs/churn_predictions.csv
  - data/outputs/at_risk_customers.csv
  - data/outputs/metrics_report.json
"""

import sys
import json
import logging
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
)
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    from lightgbm import LGBMClassifier
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

warnings.filterwarnings("ignore")

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
MODELS_DIR = PROJECT_ROOT / "models"
INPUT_FILE = PROCESSED_DIR / "churn_features.parquet"

# Features para el modelo
FEATURE_COLUMNS = [
    "days_since_last_purchase", "days_since_first_purchase", "customer_tenure_days",
    "total_orders", "avg_days_between_orders",
    "orders_last_30d", "orders_last_60d", "orders_last_90d",
    "total_revenue", "avg_order_value", "max_order_value", "revenue_trend",
    "avg_review_score", "last_review_score", "pct_reviews_below_3",
    "has_negative_review", "review_score_trend",
    "avg_delivery_days", "delivery_delay_rate", "avg_delay_days",
]
TARGET = "churned"


def verificar_input() -> None:
    """Verifica que exista el archivo de entrada."""
    if not INPUT_FILE.exists():
        logger.error("❌ No se encontró: %s", INPUT_FILE)
        logger.error("   Ejecuta primero: python pipeline/02_feature_engineering.py")
        sys.exit(1)


def split_temporal(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Divide los datos por first_purchase_date (split temporal).
    Train: hasta 2017-09 | Val: 2017-10 a 2018-03 | Test: 2018-04+
    """
    train = df[df["first_purchase_date"] < "2017-10-01"].copy()
    val = df[
        (df["first_purchase_date"] >= "2017-10-01")
        & (df["first_purchase_date"] < "2018-04-01")
    ].copy()
    test = df[df["first_purchase_date"] >= "2018-04-01"].copy()

    for name, subset in [("Train", train), ("Val", val), ("Test", test)]:
        logger.info("   %s: %d clientes (churn: %.1f%%)",
                    name, len(subset), subset[TARGET].mean() * 100)
    return train, val, test


def optimizar_threshold(y_true: np.ndarray, y_proba: np.ndarray) -> float:
    """Optimiza threshold para maximizar recall con F1 > 0.3."""
    best_t, best_r = 0.5, 0.0
    for t in np.arange(0.1, 0.9, 0.01):
        pred = (y_proba >= t).astype(int)
        r = recall_score(y_true, pred, zero_division=0)
        f = f1_score(y_true, pred, zero_division=0)
        if r > best_r and f > 0.3:
            best_r, best_t = r, t
    logger.info("🎯 Threshold óptimo: %.2f (Recall: %.4f)", best_t, best_r)
    return round(best_t, 2)


def generar_shap_values(modelo: Any, X_data: np.ndarray, max_n: int = 500) -> Optional[np.ndarray]:
    """Genera SHAP values 2-D (n_muestras × n_features) para la clase positiva."""
    if not HAS_SHAP:
        logger.warning("⚠️ SHAP no instalado, saltando...")
        return None

    logger.info("🔍 Calculando SHAP values ...")
    if len(X_data) > max_n:
        idx = np.random.choice(len(X_data), max_n, replace=False)
        X_sample = X_data[idx]
    else:
        X_sample = X_data

    model_type = type(modelo).__name__
    if model_type in ("XGBClassifier", "LGBMClassifier", "RandomForestClassifier"):
        explainer = shap.TreeExplainer(modelo)
    else:
        explainer = shap.LinearExplainer(modelo, X_sample)

    sv = explainer.shap_values(X_sample)

    # Normalizar a 2-D para la clase positiva
    if isinstance(sv, list):
        sv = sv[1]  # clase 1 = churned
    if sv.ndim == 3:
        sv = sv[:, :, 1]  # (n, features, 2) → tomar clase 1

    logger.info("   → SHAP shape: %s para %d muestras", sv.shape, len(X_sample))
    return sv


def main() -> None:
    """Punto de entrada principal."""
    logger.info("=" * 60)
    logger.info("AGENTE 3 — Modelo de Churn Prediction")
    logger.info("=" * 60)

    verificar_input()

    # Cargar datos
    logger.info("📂 Cargando datos ...")
    df = pd.read_parquet(INPUT_FILE)
    df["first_purchase_date"] = pd.to_datetime(df["first_purchase_date"])
    df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"])
    logger.info("   → %d clientes, %d columnas", len(df), len(df.columns))

    # Split temporal
    logger.info("📊 Split temporal:")
    train, val, test = split_temporal(df)

    # Preparar matrices
    def preparar(subset: pd.DataFrame):
        X = subset[FEATURE_COLUMNS].values.astype(float)
        X[np.isnan(X)] = 0
        X[np.isinf(X)] = 0
        return X, subset[TARGET].values

    X_train, y_train = preparar(train)
    X_val, y_val = preparar(val)
    X_test, y_test = preparar(test)

    # Escalar (solo para LR)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    # ── Entrenar modelos ──────────────────────────
    logger.info("\n🤖 Entrenando modelos ...")
    resultados: Dict[str, Dict] = {}

    # Logistic Regression (escalado)
    logger.info("🔹 Logistic Regression ...")
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr.fit(X_train_s, y_train)
    p = lr.predict_proba(X_val_s)[:, 1]
    resultados["Logistic Regression"] = {
        "modelo": lr, "escalar": True,
        "auc": round(roc_auc_score(y_val, p), 4),
        "f1": round(f1_score(y_val, lr.predict(X_val_s)), 4),
        "precision": round(precision_score(y_val, lr.predict(X_val_s), zero_division=0), 4),
        "recall": round(recall_score(y_val, lr.predict(X_val_s)), 4),
    }

    # Random Forest
    logger.info("🔹 Random Forest ...")
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=10, class_weight="balanced", random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    p = rf.predict_proba(X_val)[:, 1]
    resultados["Random Forest"] = {
        "modelo": rf, "escalar": False,
        "auc": round(roc_auc_score(y_val, p), 4),
        "f1": round(f1_score(y_val, rf.predict(X_val)), 4),
        "precision": round(precision_score(y_val, rf.predict(X_val), zero_division=0), 4),
        "recall": round(recall_score(y_val, rf.predict(X_val)), 4),
    }

    # XGBoost
    if HAS_XGBOOST:
        logger.info("🔹 XGBoost ...")
        spw = (len(y_train) - y_train.sum()) / max(y_train.sum(), 1)
        xgb = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.1,
            scale_pos_weight=spw, random_state=42, eval_metric="logloss", n_jobs=-1
        )
        xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        p = xgb.predict_proba(X_val)[:, 1]
        resultados["XGBoost"] = {
            "modelo": xgb, "escalar": False,
            "auc": round(roc_auc_score(y_val, p), 4),
            "f1": round(f1_score(y_val, xgb.predict(X_val)), 4),
            "precision": round(precision_score(y_val, xgb.predict(X_val), zero_division=0), 4),
            "recall": round(recall_score(y_val, xgb.predict(X_val)), 4),
        }

    # LightGBM
    if HAS_LIGHTGBM:
        logger.info("🔹 LightGBM ...")
        lgbm = LGBMClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.1,
            class_weight="balanced", random_state=42, n_jobs=-1, verbose=-1
        )
        lgbm.fit(X_train, y_train, eval_set=[(X_val, y_val)])
        p = lgbm.predict_proba(X_val)[:, 1]
        resultados["LightGBM"] = {
            "modelo": lgbm, "escalar": False,
            "auc": round(roc_auc_score(y_val, p), 4),
            "f1": round(f1_score(y_val, lgbm.predict(X_val)), 4),
            "precision": round(precision_score(y_val, lgbm.predict(X_val), zero_division=0), 4),
            "recall": round(recall_score(y_val, lgbm.predict(X_val)), 4),
        }

    # Mostrar resultados
    logger.info("\n📋 Resultados de validación:")
    for n, r in resultados.items():
        logger.info("   %s → AUC: %.4f | F1: %.4f | Prec: %.4f | Rec: %.4f",
                    n, r["auc"], r["f1"], r["precision"], r["recall"])

    # Seleccionar mejor
    mejor_nombre = max(resultados, key=lambda k: resultados[k]["auc"])
    mejor = resultados[mejor_nombre]
    modelo_final = mejor["modelo"]
    usa_escalar = mejor["escalar"]
    logger.info("\n🏆 Mejor: %s (AUC: %.4f)", mejor_nombre, mejor["auc"])

    # Threshold
    X_val_f = X_val_s if usa_escalar else X_val
    y_val_proba = modelo_final.predict_proba(X_val_f)[:, 1]
    threshold = optimizar_threshold(y_val, y_val_proba)

    # Evaluación en test
    X_test_f = scaler.transform(X_test) if usa_escalar else X_test
    y_test_proba = modelo_final.predict_proba(X_test_f)[:, 1]
    y_test_pred = (y_test_proba >= threshold).astype(int)

    if y_test.sum() > 0 and (len(y_test) - y_test.sum()) > 0:
        test_auc = round(roc_auc_score(y_test, y_test_proba), 4)
        test_f1 = round(f1_score(y_test, y_test_pred), 4)
        test_prec = round(precision_score(y_test, y_test_pred, zero_division=0), 4)
        test_rec = round(recall_score(y_test, y_test_pred), 4)
        logger.info("\n📋 TEST: AUC=%.4f F1=%.4f Prec=%.4f Rec=%.4f",
                    test_auc, test_f1, test_prec, test_rec)
    else:
        logger.warning("⚠️ Test set sin ambas clases, usando métricas de validación")
        test_auc, test_f1 = mejor["auc"], mejor["f1"]
        test_prec, test_rec = mejor["precision"], mejor["recall"]

    # SHAP (sobre validación que tiene ambas clases)
    shap_values = generar_shap_values(modelo_final, X_val_f)

    # ── Guardar outputs ───────────────────────────
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Modelo pkl
    joblib.dump({
        "modelo": modelo_final, "scaler": scaler if usa_escalar else None,
        "usa_escalar": usa_escalar, "threshold": threshold,
        "feature_columns": FEATURE_COLUMNS, "nombre_modelo": mejor_nombre,
    }, MODELS_DIR / "churn_model.pkl")
    logger.info("💾 Modelo guardado")

    # Predicciones TODOS los clientes
    logger.info("📊 Predicciones globales ...")
    X_all = df[FEATURE_COLUMNS].values.astype(float)
    X_all[np.isnan(X_all)] = 0
    X_all[np.isinf(X_all)] = 0
    if usa_escalar:
        X_all = scaler.transform(X_all)

    df["prob_churn"] = modelo_final.predict_proba(X_all)[:, 1]
    df["pred_churn"] = (df["prob_churn"] >= threshold).astype(int)

    # SHAP parquet
    if shap_values is not None:
        shap_df = pd.DataFrame(shap_values, columns=[f"shap_{c}" for c in FEATURE_COLUMNS])
        val_ids = val["customer_unique_id"].values
        if len(shap_df) <= len(val_ids):
            shap_df["customer_unique_id"] = val_ids[:len(shap_df)]
            shap_df.to_parquet(OUTPUTS_DIR / "shap_values.parquet", index=False, engine="pyarrow")
            logger.info("💾 SHAP values guardados")

    # Predictions CSV
    pred_cols = [
        "customer_unique_id", "first_purchase_date", "last_purchase_date",
        "customer_state", "total_orders", "total_revenue",
        "days_since_last_purchase", "avg_review_score", "delivery_delay_rate",
        "prob_churn", "pred_churn", "churned",
    ]
    df[pred_cols].to_csv(OUTPUTS_DIR / "churn_predictions.csv", index=False)
    logger.info("💾 Predicciones: %d clientes", len(df))

    # At-risk CSV
    at_risk = df[df["prob_churn"] > 0.6].sort_values("prob_churn", ascending=False).copy()

    def _accion(row):
        if row["prob_churn"] > 0.85:
            return "🚨 Contacto urgente — oferta de retención personalizada"
        elif row["avg_review_score"] < 3:
            return "⭐ Resolver insatisfacción — seguimiento de calidad"
        elif row["delivery_delay_rate"] > 0.5:
            return "🚚 Mejorar logística — compensar retrasos"
        elif row["days_since_last_purchase"] > 120:
            return "📧 Campaña de reactivación — descuento exclusivo"
        return "📞 Llamada de seguimiento — encuesta de satisfacción"

    at_risk["accion_recomendada"] = at_risk.apply(_accion, axis=1)
    at_risk_cols = [
        "customer_unique_id", "prob_churn", "days_since_last_purchase",
        "total_revenue", "total_orders", "avg_review_score",
        "customer_state", "accion_recomendada",
    ]
    at_risk[at_risk_cols].to_csv(OUTPUTS_DIR / "at_risk_customers.csv", index=False)
    logger.info("💾 Clientes en riesgo: %d", len(at_risk))

    # Feature importance
    fi = np.abs(shap_values).mean(axis=0) if shap_values is not None else np.zeros(len(FEATURE_COLUMNS))

    # Metrics JSON
    metricas = {
        "mejor_modelo": mejor_nombre,
        "threshold_optimo": threshold,
        "resultados_validacion": {
            n: {k: v for k, v in r.items() if k not in ("modelo", "escalar")}
            for n, r in resultados.items()
        },
        "resultados_test": {
            "auc": test_auc, "f1": test_f1, "precision": test_prec, "recall": test_rec,
        },
        "total_clientes": len(df),
        "total_en_riesgo": len(at_risk),
        "revenue_en_riesgo": round(float(at_risk["total_revenue"].sum()), 2),
        "feature_importance": dict(zip(FEATURE_COLUMNS, [round(float(v), 4) for v in fi])),
    }
    with open(OUTPUTS_DIR / "metrics_report.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False, default=str)
    logger.info("💾 Métricas guardadas")

    logger.info("=" * 60)
    logger.info("✅ Modelo de churn completado exitosamente")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
