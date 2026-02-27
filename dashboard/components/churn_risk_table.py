"""
churn_risk_table.py — At-Risk Customers (Optimized)
=====================================================
Shows top 10 highest-priority customers by revenue × churn probability,
with a risk scatter for overview.
"""

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translations import t  # noqa: E402
from utils import apply_chart_theme  # noqa: E402


def render_risk_scatter(at_risk: pd.DataFrame) -> None:
    """Render churn probability vs revenue scatter — top priority overview."""
    if at_risk.empty:
        return

    # Summary KPIs
    total = len(at_risk)
    rev = at_risk["total_revenue"].sum() if "total_revenue" in at_risk.columns else 0
    rev_display = f"R$ {rev / 1_000_000:.1f}M" if rev >= 1_000_000 else f"R$ {rev:,.0f}"

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="content-card" style="text-align:center;">
            <div style="color:#8A7A6A;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.05em">{t("total_at_risk")}</div>
            <div style="font-family:'Space Grotesk';font-size:2rem;font-weight:700;color:#CD4631">{total:,}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="content-card" style="text-align:center;">
            <div style="color:#8A7A6A;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.05em">{t("revenue_at_risk_label")}</div>
            <div style="font-family:'Space Grotesk';font-size:2rem;font-weight:700;color:#CD4631">{rev_display}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Scatter — show all but highlight top 10
    if "prob_churn" in at_risk.columns and "total_revenue" in at_risk.columns:
        # Top 10 priority (by revenue × churn prob)
        at_risk_sorted = at_risk.copy()
        at_risk_sorted["priority_score"] = at_risk_sorted["prob_churn"] * at_risk_sorted["total_revenue"]
        top10 = at_risk_sorted.nlargest(10, "priority_score")
        rest = at_risk_sorted.drop(top10.index)

        fig = go.Figure()

        # Background dots
        if len(rest) > 0:
            fig.add_trace(go.Scattergl(
                x=rest["prob_churn"], y=rest["total_revenue"],
                mode="markers",
                marker=dict(size=5, color="#DEA47E", opacity=0.25),
                name="Others", showlegend=False,
                hovertemplate="Prob: %{x:.1%}<br>Revenue: R$ %{y:,.0f}<extra></extra>",
            ))

        # Top 10 highlighted
        fig.add_trace(go.Scattergl(
            x=top10["prob_churn"], y=top10["total_revenue"],
            mode="markers+text",
            marker=dict(size=14, color="#CD4631", line=dict(width=2, color="#FFFFFF")),
            text=list(range(1, len(top10) + 1)),
            textposition="middle center",
            textfont=dict(size=8, color="#FFFFFF"),
            name="Top 10 Priority",
            customdata=top10[["customer_unique_id"]].values if "customer_unique_id" in top10.columns else None,
            hovertemplate="<b>#%{text}</b><br>Prob: %{x:.1%}<br>Revenue: R$ %{y:,.0f}<extra></extra>",
        ))

        fig = apply_chart_theme(fig, t("chart_risk_scatter"))
        fig.update_layout(
            height=380,
            xaxis_title=t("col_prob_churn"),
            yaxis_title=t("col_revenue"),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_risk_table(at_risk: pd.DataFrame) -> None:
    """Render top 10 at-risk customers as prioritized cards + export for full list."""
    if at_risk.empty:
        return

    # Calculate priority score
    at_risk_sorted = at_risk.copy()
    if "prob_churn" in at_risk.columns and "total_revenue" in at_risk.columns:
        at_risk_sorted["priority_score"] = at_risk_sorted["prob_churn"] * at_risk_sorted["total_revenue"]
        at_risk_sorted = at_risk_sorted.nlargest(10, "priority_score")
    else:
        at_risk_sorted = at_risk_sorted.head(10)

    # Display as clean table with key columns only
    cols_map = {}
    if "customer_unique_id" in at_risk_sorted.columns:
        cols_map["customer_unique_id"] = t("col_customer")
    if "prob_churn" in at_risk_sorted.columns:
        cols_map["prob_churn"] = t("col_prob_churn")
    if "total_revenue" in at_risk_sorted.columns:
        cols_map["total_revenue"] = t("col_revenue")
    if "days_since_last_purchase" in at_risk_sorted.columns:
        cols_map["days_since_last_purchase"] = t("col_days_inactive")
    if "avg_review_score" in at_risk_sorted.columns:
        cols_map["avg_review_score"] = t("col_review")
    if "accion_recomendada" in at_risk_sorted.columns:
        cols_map["accion_recomendada"] = t("col_action")

    show_cols = [c for c in cols_map if c in at_risk_sorted.columns]
    display = at_risk_sorted[show_cols].rename(columns=cols_map).copy()

    # Format
    prob_col = t("col_prob_churn")
    if prob_col in display.columns:
        display[prob_col] = display[prob_col].apply(lambda x: f"{x:.1%}")
    rev_col = t("col_revenue")
    if rev_col in display.columns:
        display[rev_col] = display[rev_col].apply(lambda x: f"R$ {x:,.0f}")
    review_col = t("col_review")
    if review_col in display.columns:
        display[review_col] = display[review_col].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")

    # Truncate customer IDs for readability
    cust_col = t("col_customer")
    if cust_col in display.columns:
        display[cust_col] = display[cust_col].apply(lambda x: x[:12] + "..." if len(str(x)) > 12 else x)

    st.markdown(f"**Top 10 — {t('total_at_risk')}**")
    st.dataframe(display, use_container_width=True, height=400)

    # Export FULL list
    csv = at_risk.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t("btn_export"),
        data=csv,
        file_name="at_risk_customers_export.csv",
        mime="text/csv",
    )
