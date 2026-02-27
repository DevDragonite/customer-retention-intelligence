"""
model_explainer.py — Model Performance & SHAP Explainability
=============================================================
Renders model metrics, SHAP feature importance, and explanations.
"""

from typing import Dict, Any

import plotly.graph_objects as go
import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translations import t  # noqa: E402
from utils import apply_chart_theme  # noqa: E402


def render_model_metrics(metrics: Dict[str, Any]) -> None:
    """Render model performance metrics in glass cards."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    test_res = metrics.get("resultados_test", {})
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        auc = test_res.get("auc", 0)
        st.metric(t("model_auc"), f"{auc * 100:.1f}%" if auc <= 1 else f"{auc:.1f}%")
    with col2:
        f1 = test_res.get("f1", 0)
        st.metric(t("model_f1"), f"{f1 * 100:.1f}%" if f1 <= 1 else f"{f1:.1f}%")
    with col3:
        prec = test_res.get("precision", 0)
        st.metric(t("model_precision"), f"{prec * 100:.1f}%" if prec <= 1 else f"{prec:.1f}%")
    with col4:
        rec = test_res.get("recall", 0)
        st.metric(t("model_recall"), f"{rec * 100:.1f}%" if rec <= 1 else f"{rec:.1f}%")

    st.markdown('</div>', unsafe_allow_html=True)

    # Model info
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.metric(t("model_best"), metrics.get("mejor_modelo", "N/A"))
    with info_col2:
        st.metric(t("model_threshold"), f"{metrics.get('threshold_optimo', 0.5):.2f}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_feature_importance(metrics: Dict[str, Any]) -> None:
    """Render SHAP-based feature importance bar chart."""
    fi = metrics.get("feature_importance", {})
    if not fi:
        return

    # Sort by importance
    sorted_fi = sorted(fi.items(), key=lambda x: abs(x[1]), reverse=True)[:15]
    features = [f[0] for f in reversed(sorted_fi)]
    importances = [f[1] for f in reversed(sorted_fi)]

    # Color gradient from low to high importance
    max_imp = max(importances) if importances else 1
    colors = []
    for imp in importances:
        ratio = imp / max_imp
        if ratio > 0.7:
            colors.append("#CD4631")
        elif ratio > 0.4:
            colors.append("#DEA47E")
        else:
            colors.append("#81ADC8")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=importances,
        y=features,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x:.4f}<extra></extra>",
    ))

    fig = apply_chart_theme(fig, t("feature_importance_title"))
    fig.update_layout(height=500, yaxis=dict(tickfont=dict(size=11)))
    st.plotly_chart(fig, use_container_width=True)


def render_shap_waterfall(metrics: Dict[str, Any]) -> None:
    """Render SHAP waterfall chart for a single customer (placeholder)."""
    pass
