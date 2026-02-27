"""
app.py — Customer Retention Intelligence Dashboard
====================================================
Premium SaaS-level Streamlit dashboard with glassmorphism UI,
trilingual support (ES/EN/PT), storytelling narratives, and
performance-optimized lazy loading.
"""

import sys
from pathlib import Path

import streamlit as st

# ── Page config MUST be first Streamlit command ──
st.set_page_config(
    page_title="Customer Retention Intelligence",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add project root and dashboard to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(DASHBOARD_DIR))

from translations import t  # noqa: E402
from utils import (  # noqa: E402
    load_predictions,
    load_at_risk,
    load_metrics,
    load_cohort_matrix,
    load_insights,
    load_features,
    apply_chart_theme,
)
from components.kpi_cards import render_kpi_cards, render_churn_trend, render_top_states  # noqa: E402
from components.cohort_heatmap import render_cohort_heatmap, render_retention_curves, render_cohort_comparison  # noqa: E402
from components.churn_risk_table import render_risk_table, render_risk_scatter  # noqa: E402
from components.model_explainer import render_model_metrics, render_feature_importance  # noqa: E402
from components.geo_map import render_churn_map, render_delivery_vs_churn  # noqa: E402

# ── Session state defaults ──
if "language" not in st.session_state:
    st.session_state["language"] = "ES"

# ══════════════════════════════════════════════════
# GLOBAL CSS — Glassmorphism + Premium UI
# ══════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');
*{font-family:'Inter',sans-serif}
h1,h2,h3{font-family:'Space Grotesk',sans-serif}
.stApp{background:linear-gradient(135deg,#1C1410 0%,#2E1F14 50%,#1C1410 100%);background-attachment:fixed}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#2E1F14 0%,#1C1410 100%);border-right:1px solid rgba(158,98,64,0.3)}
[data-testid="stSidebar"] *{color:#F8F2DC !important}
.glass-card{background:rgba(158,98,64,0.08);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(222,164,126,0.2);border-radius:16px;padding:24px;margin:8px 0;transition:all 0.3s ease}
.glass-card:hover{border-color:rgba(222,164,126,0.5);background:rgba(158,98,64,0.14);transform:translateY(-2px);box-shadow:0 8px 32px rgba(205,70,49,0.15)}
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif !important;font-size:2.2rem !important;font-weight:700 !important;color:#DEA47E !important;text-shadow:0 0 20px rgba(222,164,126,0.4)}
[data-testid="stMetricLabel"]{color:#F8F2DC !important;opacity:0.7;font-size:0.8rem !important;text-transform:uppercase;letter-spacing:0.1em}
[data-testid="stMetricDelta"] > div{color:#81ADC8 !important;font-size:0.85rem !important}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:rgba(28,20,16,0.6);border-radius:12px;padding:4px;gap:4px;border:1px solid rgba(158,98,64,0.2)}
[data-testid="stTabs"] [data-baseweb="tab"]{background:transparent;border-radius:8px;color:rgba(248,242,220,0.6) !important;font-weight:500;padding:8px 16px;transition:all 0.2s}
[data-testid="stTabs"] [aria-selected="true"]{background:linear-gradient(135deg,#9E6240,#CD4631) !important;color:#F8F2DC !important;box-shadow:0 4px 12px rgba(205,70,49,0.3)}
[data-testid="stDataFrame"]{border:1px solid rgba(158,98,64,0.2);border-radius:12px;overflow:hidden}
[data-baseweb="select"] > div{background:rgba(28,20,16,0.8) !important;border-color:rgba(158,98,64,0.3) !important;color:#F8F2DC !important}
[data-testid="stButton"] button{background:linear-gradient(135deg,#9E6240,#CD4631) !important;border:none !important;color:#F8F2DC !important;border-radius:8px !important;font-weight:600 !important;padding:8px 20px !important;transition:all 0.2s !important}
[data-testid="stButton"] button:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(205,70,49,0.4) !important}
.dashboard-header{background:linear-gradient(135deg,rgba(158,98,64,0.15),rgba(205,70,49,0.1));border:1px solid rgba(222,164,126,0.2);border-radius:20px;padding:32px 40px;margin-bottom:24px;text-align:center}
.dashboard-header h1{font-size:2.2rem;font-weight:700;background:linear-gradient(135deg,#DEA47E,#F8F2DC);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0}
.dashboard-header p{color:rgba(248,242,220,0.6);font-size:1rem;margin-top:8px}
.badge-high{background:rgba(205,70,49,0.2);color:#CD4631;border:1px solid rgba(205,70,49,0.4);border-radius:20px;padding:2px 12px;font-size:0.75rem;font-weight:600;display:inline-block}
.badge-medium{background:rgba(222,164,126,0.2);color:#DEA47E;border:1px solid rgba(222,164,126,0.4);border-radius:20px;padding:2px 12px;font-size:0.75rem;font-weight:600;display:inline-block}
.badge-low{background:rgba(129,173,200,0.2);color:#81ADC8;border:1px solid rgba(129,173,200,0.4);border-radius:20px;padding:2px 12px;font-size:0.75rem;font-weight:600;display:inline-block}
.insight-box{background:rgba(129,173,200,0.08);border-left:3px solid #81ADC8;border-radius:0 12px 12px 0;padding:16px 20px;margin:16px 0;color:rgba(248,242,220,0.85);font-size:0.92rem;line-height:1.6}
.lang-btn{display:inline-flex;align-items:center;gap:6px;cursor:pointer}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:rgba(28,20,16,0.5)}
::-webkit-scrollbar-thumb{background:rgba(158,98,64,0.5);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#9E6240}
[data-testid="stSlider"] label{color:#F8F2DC !important}
[data-testid="stPopover"] > button{background:rgba(158,98,64,0.15) !important;border:1px solid rgba(222,164,126,0.3) !important;border-radius:8px !important;padding:4px 10px !important;color:#F8F2DC !important;font-weight:600 !important;font-size:0.85rem !important}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# COMPACT LANGUAGE SELECTOR (only 2 other options)
# ══════════════════════════════════════════════════
def language_selector():
    """Compact language selector showing only 2 non-active options."""
    flags = {"ES": "🇪🇸", "EN": "🇬🇧", "PT": "🇧🇷"}
    labels = {"ES": "ES", "EN": "EN", "PT": "PT"}
    active = st.session_state["language"]
    others = [l for l in flags if l != active]

    with st.popover(f"{flags[active]} {active}"):
        for lang_code in others:
            if st.button(
                f"{flags[lang_code]}  {labels[lang_code]}",
                key=f"lang_{lang_code}",
                use_container_width=True,
            ):
                st.session_state["language"] = lang_code
                st.rerun()


import re

def md_to_html(text: str) -> str:
    """Convert markdown bold/code to HTML, and newlines to <br>."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code style="background:rgba(158,98,64,0.2);padding:2px 6px;border-radius:4px;font-size:0.85em;color:#DEA47E">\1</code>', text)
    text = text.replace("\n", "<br>")
    return text


def section_insight(key: str):
    """Render a storytelling insight box for a given section."""
    st.markdown(
        f'<div class="insight-box">{md_to_html(t(key))}</div>',
        unsafe_allow_html=True,
    )


def story_card(icon: str, title: str, body: str):
    """Render a glass-card section for conclusions."""
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color:#DEA47E;margin:0 0 12px;">{icon} {title}</h3>
        <div style="color:rgba(248,242,220,0.85);line-height:1.8;font-size:0.95rem;">
            {md_to_html(body)}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# HEADER + LANG SELECTOR
# ══════════════════════════════════════════════════
h1, h2 = st.columns([12, 1])
with h1:
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>🔄 {t("app_title")}</h1>
        <p>{t("app_subtitle")}</p>
    </div>
    """, unsafe_allow_html=True)
with h2:
    language_selector()


# ══════════════════════════════════════════════════
# STORYTELLING INTRO
# ══════════════════════════════════════════════════
st.markdown(f"""
<div class="glass-card">
    <h3 style="color:#DEA47E;margin:0 0 12px;">{t("intro_title")}</h3>
    <div style="color:rgba(248,242,220,0.85);line-height:1.8;font-size:0.95rem;">
        {md_to_html(t("intro_body"))}
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 28px;">
        <div style="font-size:2.5rem">🔄</div>
        <div style="font-family:'Space Grotesk';font-size:1.1rem;font-weight:700;color:#DEA47E;">
            {t("sidebar_title")}
        </div>
        <div style="font-size:0.7rem;color:rgba(248,242,220,0.4);margin-top:4px;">
            {t("sidebar_subtitle")}
        </div>
    </div>
    <hr style="border-color:rgba(158,98,64,0.2);margin-bottom:24px;">
    """, unsafe_allow_html=True)

    st.markdown(f"### {t('sidebar_filters')}")

    # ── PERFORMANCE: Load only predictions for sidebar filter ──
    predictions = load_predictions()
    if predictions is not None and "customer_state" in predictions.columns:
        states = sorted(predictions["customer_state"].dropna().unique().tolist())
        selected_state = st.selectbox(
            t("filter_state"),
            [t("filter_all_states")] + states,
            key="filter_state_select",
        )
    else:
        selected_state = t("filter_all_states")

    threshold = st.slider(
        t("filter_threshold"), 0.0, 1.0, 0.6, 0.05,
        key="risk_threshold",
    )

    st.markdown(f"""
    <hr style="border-color:rgba(158,98,64,0.2);margin-top:24px;">
    <div style="text-align:center;padding:12px 0;">
        <div style="font-size:0.7rem;color:rgba(248,242,220,0.3);">
            {t("sidebar_footer").replace(chr(10),"<br>")}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# LOAD SHARED DATA (cached, loads once)
# ══════════════════════════════════════════════════
insights = load_insights()
metrics = load_metrics()


# ══════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("tab_overview"),
    t("tab_cohort"),
    t("tab_atrisk"),
    t("tab_model"),
    t("tab_geo"),
    t("tab_insights"),
])

# ── Tab 1: Executive Overview ──
with tab1:
    if insights:
        render_kpi_cards(insights)
        section_insight("insight_overview")
        col_trend, col_states = st.columns([3, 2])
        with col_trend:
            render_churn_trend(insights)
        with col_states:
            render_top_states(insights)
    else:
        st.warning(t("no_data"))

# ── Tab 2: Cohort Retention (lazy load) ──
with tab2:
    cohort_df = load_cohort_matrix()
    if cohort_df is not None and not cohort_df.empty:
        render_cohort_comparison(insights or {})
        section_insight("insight_cohort")
        render_cohort_heatmap(cohort_df)
        render_retention_curves(cohort_df)
    else:
        st.warning(t("no_data"))

# ── Tab 3: At-Risk Customers (lazy load) ──
with tab3:
    at_risk = load_at_risk()
    if at_risk is not None and not at_risk.empty:
        section_insight("insight_atrisk")
        render_risk_scatter(at_risk)
        st.markdown("")
        render_risk_table(at_risk)
    else:
        st.warning(t("no_data"))

# ── Tab 4: Model Explainer ──
with tab4:
    if metrics:
        render_model_metrics(metrics)
        section_insight("insight_model")
        render_feature_importance(metrics)
    else:
        st.warning(t("no_data"))

# ── Tab 5: Geo Intelligence (lazy load) ──
with tab5:
    if insights and "churn_por_estado" in insights:
        section_insight("insight_geo")
        render_churn_map(predictions, insights["churn_por_estado"])
        features_df = load_features()
        if features_df is not None:
            # Apply state filter
            if selected_state != t("filter_all_states") and "customer_state" in features_df.columns:
                features_df = features_df[features_df["customer_state"] == selected_state]
            render_delivery_vs_churn(features_df)
    else:
        st.warning(t("no_data"))

# ── Tab 6: Conclusions ──
with tab6:
    st.markdown(
        f'<h2 style="color:#DEA47E;font-family:Space Grotesk;margin-bottom:20px;">'
        f'{t("conclusions_title")}</h2>',
        unsafe_allow_html=True,
    )

    # Causes
    story_card("🔎", t("conclusions_causes_title").replace("🔎 ", ""), t("conclusions_causes"))
    st.markdown("")

    # Key Findings
    st.markdown(
        f'<div class="glass-card">'
        f'<h3 style="color:#DEA47E;margin:0 0 12px;">{t("conclusions_findings_title")}</h3>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(t("conclusions_findings"))
    st.markdown("")

    # Recommended Actions
    story_card("🚀", t("conclusions_actions_title").replace("🚀 ", ""), t("conclusions_actions"))
    st.markdown("")

    # Prediction
    story_card("🔮", t("conclusions_prediction_title").replace("🔮 ", ""), t("conclusions_prediction"))
