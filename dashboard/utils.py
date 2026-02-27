"""
utils.py — Dashboard Utilities
================================
Cached data loading functions and shared chart theme for the
Customer Retention Intelligence dashboard.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ──────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "data" / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"


# ══════════════════════════════════════════════════
# CACHED DATA LOADING
# ══════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_features() -> Optional[pd.DataFrame]:
    """Load churn features parquet."""
    path = PROCESSED_DIR / "churn_features.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None


@st.cache_data(ttl=3600)
def load_predictions() -> Optional[pd.DataFrame]:
    """Load churn predictions CSV."""
    path = OUTPUTS_DIR / "churn_predictions.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


@st.cache_data(ttl=3600)
def load_at_risk() -> Optional[pd.DataFrame]:
    """Load at-risk customers CSV."""
    path = OUTPUTS_DIR / "at_risk_customers.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


@st.cache_data(ttl=3600)
def load_metrics() -> Optional[Dict[str, Any]]:
    """Load metrics report JSON."""
    path = OUTPUTS_DIR / "metrics_report.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_data(ttl=3600)
def load_cohort_matrix() -> Optional[pd.DataFrame]:
    """Load cohort retention matrix parquet."""
    path = PROCESSED_DIR / "cohort_matrix.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None


@st.cache_data(ttl=3600)
def load_revenue_cohort_matrix() -> Optional[pd.DataFrame]:
    """Load revenue cohort matrix parquet."""
    path = PROCESSED_DIR / "revenue_cohort_matrix.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None


@st.cache_data(ttl=3600)
def load_insights() -> Optional[Dict[str, Any]]:
    """Load dashboard insights JSON."""
    path = OUTPUTS_DIR / "dashboard_insights.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_data(ttl=3600)
def load_cohort_insights() -> Optional[Dict[str, Any]]:
    """Load cohort insights JSON."""
    path = OUTPUTS_DIR / "cohort_insights.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ══════════════════════════════════════════════════
# CHART THEME
# ══════════════════════════════════════════════════

def apply_chart_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply the unified premium Plotly theme to any figure."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Space Grotesk", size=16, color="#9E6240"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.6)",
        font=dict(family="Inter", color="#2E1F14"),
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(158,98,64,0.15)",
            borderwidth=1,
            font=dict(color="#2E1F14"),
        ),
        xaxis=dict(
            gridcolor="rgba(158,98,64,0.1)",
            linecolor="rgba(158,98,64,0.2)",
        ),
        yaxis=dict(
            gridcolor="rgba(158,98,64,0.1)",
            linecolor="rgba(158,98,64,0.2)",
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


# ══════════════════════════════════════════════════
# RISK BADGES
# ══════════════════════════════════════════════════

def get_risk_badge(prob: float, lang: str = "ES") -> str:
    """Return an HTML risk badge (high/medium/low) based on churn probability."""
    labels = {
        "ES": {"high": "ALTO", "medium": "MEDIO", "low": "BAJO"},
        "EN": {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"},
        "PT": {"high": "ALTO", "medium": "MÉDIO", "low": "BAIXO"},
    }
    lb = labels.get(lang, labels["ES"])
    if prob >= 0.7:
        return f'<span class="badge-high">🔴 {lb["high"]}</span>'
    elif prob >= 0.4:
        return f'<span class="badge-medium">🟡 {lb["medium"]}</span>'
    else:
        return f'<span class="badge-low">🟢 {lb["low"]}</span>'
