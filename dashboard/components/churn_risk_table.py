"""
churn_risk_table.py — At-Risk Customers Table & Scatter
========================================================
Displays at-risk customers with risk badges and prioritization scatter.
"""

from typing import Dict, Any

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translations import t  # noqa: E402
from utils import apply_chart_theme, get_risk_badge  # noqa: E402


def render_risk_scatter(at_risk: pd.DataFrame) -> None:
    """Render churn probability vs revenue scatter plot for prioritization."""
    if at_risk.empty:
        return

    lang = st.session_state.get("language", "ES")

    # KPI summary
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t("total_at_risk"), f"{len(at_risk):,}")
    with col2:
        rev = at_risk["total_revenue"].sum() if "total_revenue" in at_risk.columns else 0
        if rev >= 1_000_000:
            st.metric(t("revenue_at_risk_label"), f"R$ {rev / 1_000_000:.1f}M")
        else:
            st.metric(t("revenue_at_risk_label"), f"R$ {rev:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")

    # Scatter plot
    fig = go.Figure()

    # Color by risk level
    if "prob_churn" in at_risk.columns and "total_revenue" in at_risk.columns:
        colors = []
        for p in at_risk["prob_churn"]:
            if p >= 0.7:
                colors.append("#CD4631")
            elif p >= 0.4:
                colors.append("#DEA47E")
            else:
                colors.append("#81ADC8")

        fig.add_trace(go.Scatter(
            x=at_risk["prob_churn"],
            y=at_risk["total_revenue"],
            mode="markers",
            marker=dict(
                size=8,
                color=colors,
                opacity=0.7,
                line=dict(width=1, color="rgba(248,242,220,0.3)"),
            ),
            hovertemplate=(
                f"<b>{t('col_customer')}</b>: %{{customdata[0]}}<br>"
                f"{t('col_prob_churn')}: %{{x:.1%}}<br>"
                f"{t('col_revenue')}: R$ %{{y:,.2f}}<br>"
                "<extra></extra>"
            ),
            customdata=at_risk[["customer_unique_id"]].values if "customer_unique_id" in at_risk.columns else None,
        ))

    fig = apply_chart_theme(fig, t("chart_risk_scatter"))
    fig.update_layout(
        height=400,
        xaxis_title=t("col_prob_churn"),
        yaxis_title=t("col_revenue"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_risk_table(at_risk: pd.DataFrame) -> None:
    """Render the at-risk customers table with badges and export button."""
    if at_risk.empty:
        return

    lang = st.session_state.get("language", "ES")

    # Show top 100
    display_df = at_risk.head(100).copy()

    # Build display columns
    cols_map = {}
    if "customer_unique_id" in display_df.columns:
        cols_map["customer_unique_id"] = t("col_customer")
    if "prob_churn" in display_df.columns:
        cols_map["prob_churn"] = t("col_prob_churn")
    if "days_since_last_purchase" in display_df.columns:
        cols_map["days_since_last_purchase"] = t("col_days_inactive")
    if "total_revenue" in display_df.columns:
        cols_map["total_revenue"] = t("col_revenue")
    if "total_orders" in display_df.columns:
        cols_map["total_orders"] = t("col_orders")
    if "avg_review_score" in display_df.columns:
        cols_map["avg_review_score"] = t("col_review")
    if "customer_state" in display_df.columns:
        cols_map["customer_state"] = t("col_state")
    if "accion_recomendada" in display_df.columns:
        cols_map["accion_recomendada"] = t("col_action")

    show_cols = [c for c in cols_map.keys() if c in display_df.columns]
    renamed = display_df[show_cols].rename(columns=cols_map)

    # Format prob_churn as percentage
    prob_col = t("col_prob_churn")
    if prob_col in renamed.columns:
        renamed[prob_col] = renamed[prob_col].apply(lambda x: f"{x:.1%}")

    rev_col = t("col_revenue")
    if rev_col in renamed.columns:
        renamed[rev_col] = renamed[rev_col].apply(lambda x: f"R$ {x:,.2f}")

    st.dataframe(renamed, use_container_width=True, height=400)

    # Export button
    csv = at_risk.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t("btn_export"),
        data=csv,
        file_name="at_risk_customers_export.csv",
        mime="text/csv",
    )
