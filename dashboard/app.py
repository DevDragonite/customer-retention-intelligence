"""
app.py — Customer Retention Intelligence Dashboard
====================================================
Premium SaaS-level Streamlit dashboard with cream/warm palette,
trilingual support (ES/EN/PT), storytelling narratives, and
performance-optimized lazy loading.
"""

import re
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
from components.geo_map import render_churn_map, render_delivery_vs_churn  # noqa: E402

# ── Session state defaults ──
if "language" not in st.session_state:
    st.session_state["language"] = "ES"

# ══════════════════════════════════════════════════
# GLOBAL CSS — Cream BG + Dark Sidebar (matching reference)
# ══════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');
*{font-family:'Inter',sans-serif}
h1,h2,h3{font-family:'Space Grotesk',sans-serif}

/* ── Main area: cream background ── */
.stApp{background:#F5EDD6}
[data-testid="stMainBlockContainer"]{background:#F5EDD6}

/* ── Sidebar: dark ── */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#2E1F14 0%,#1C1410 100%);border-right:1px solid rgba(158,98,64,0.3)}
[data-testid="stSidebar"] *{color:#F8F2DC !important}
[data-testid="stSidebar"] [data-testid="stMetricValue"]{color:#DEA47E !important}
[data-testid="stSidebar"] [data-baseweb="select"] > div{background:rgba(158,98,64,0.15) !important;border-color:rgba(158,98,64,0.3) !important}

/* ── Content cards ── */
.content-card{background:#FFFFFF;border-radius:16px;padding:24px;margin:8px 0;box-shadow:0 2px 12px rgba(158,98,64,0.08);border:1px solid rgba(158,98,64,0.08)}
.content-card:hover{box-shadow:0 4px 20px rgba(158,98,64,0.15);transform:translateY(-1px);transition:all 0.2s ease}

/* ── KPI cards (colored backgrounds) ── */
.kpi-card{border-radius:14px;padding:20px 24px;text-align:left;color:#FFFFFF;min-height:90px}
.kpi-card .kpi-label{font-size:0.78rem;text-transform:uppercase;letter-spacing:0.06em;opacity:0.85;margin-bottom:6px}
.kpi-card .kpi-value{font-family:'Space Grotesk',sans-serif;font-size:1.9rem;font-weight:700;line-height:1.1}
.kpi-1{background:linear-gradient(135deg,#9E6240,#7D4E32)}
.kpi-2{background:linear-gradient(135deg,#DEA47E,#C48B65)}
.kpi-3{background:linear-gradient(135deg,#81ADC8,#6A96B1)}
.kpi-4{background:linear-gradient(135deg,#CD4631,#A83828)}

/* ── Metrics override for light bg ── */
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif !important;font-size:1.8rem !important;font-weight:700 !important;color:#2E1F14 !important}
[data-testid="stMetricLabel"]{color:#5A4A3A !important;font-size:0.8rem !important;text-transform:uppercase;letter-spacing:0.08em}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:#FFFFFF;border-radius:12px;padding:4px;gap:4px;border:1px solid rgba(158,98,64,0.15);box-shadow:0 1px 4px rgba(0,0,0,0.04);display:flex;width:100%}
[data-testid="stTabs"] [data-baseweb="tab"]{background:transparent;border-radius:8px;color:#5A4A3A !important;font-weight:500;padding:10px 18px;transition:all 0.2s;flex:1;text-align:center;justify-content:center}
[data-testid="stTabs"] [aria-selected="true"]{background:linear-gradient(135deg,#9E6240,#CD4631) !important;color:#FFFFFF !important;box-shadow:0 2px 8px rgba(205,70,49,0.25)}

/* ── Table ── */
[data-testid="stDataFrame"]{border:1px solid rgba(158,98,64,0.12);border-radius:12px;overflow:hidden}

/* ── Buttons ── */
[data-testid="stButton"] button{background:linear-gradient(135deg,#9E6240,#CD4631) !important;border:none !important;color:#FFFFFF !important;border-radius:8px !important;font-weight:600 !important;padding:8px 20px !important;transition:all 0.2s !important}
[data-testid="stButton"] button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(205,70,49,0.3) !important}

/* ── Header ── */
.dashboard-header{background:#FFFFFF;border:1px solid rgba(158,98,64,0.1);border-radius:20px;padding:28px 36px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(158,98,64,0.06)}
.dashboard-header h1{font-size:1.6rem;font-weight:700;color:#2E1F14;margin:0}
.dashboard-header p{color:#8A7A6A;font-size:0.88rem;margin:4px 0 0}

/* ── Insight box ── */
.insight-box{background:rgba(129,173,200,0.1);border-left:3px solid #81ADC8;border-radius:0 10px 10px 0;padding:14px 18px;margin:14px 0;color:#3A4A5A;font-size:0.9rem;line-height:1.6}
.insight-box strong{color:#2E1F14}
.insight-box code{background:rgba(158,98,64,0.12);padding:2px 6px;border-radius:4px;font-size:0.85em;color:#9E6240}

/* ── Intro story ── */
.intro-card{background:#FFFFFF;border-radius:16px;padding:28px 32px;margin-bottom:20px;border:1px solid rgba(158,98,64,0.1);box-shadow:0 2px 12px rgba(158,98,64,0.06)}
.intro-card h3{color:#9E6240;font-size:1.15rem;margin:0 0 12px}
.intro-card p, .intro-card div{color:#2E1F14 !important;line-height:1.75;font-size:1.02rem;margin:0;font-weight:500}

/* ── Conclusion cards ── */
.story-card{background:#FFFFFF;border-radius:16px;padding:24px 28px;margin:10px 0;border:1px solid rgba(158,98,64,0.1);box-shadow:0 2px 10px rgba(158,98,64,0.06)}
.story-card:hover{box-shadow:0 4px 16px rgba(158,98,64,0.12)}
.story-card h3{color:#9E6240;margin:0 0 12px}
.story-card p,.story-card div{color:#4A3A2A;line-height:1.7;font-size:0.93rem}
.story-card strong{color:#2E1F14}

/* ── Selects (light) ── */
[data-baseweb="select"] > div{background:#FFFFFF !important;border-color:rgba(158,98,64,0.2) !important;color:#2E1F14 !important}

/* ── Popover ── */
[data-testid="stPopover"] > button{background:#FFFFFF !important;border:1px solid rgba(158,98,64,0.2) !important;border-radius:8px !important;padding:6px 12px !important;color:#2E1F14 !important;font-weight:600 !important;font-size:0.85rem !important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#F5EDD6}
::-webkit-scrollbar-thumb{background:rgba(158,98,64,0.3);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#9E6240}

/* ── Slider ── */
[data-testid="stSlider"] label{color:#F8F2DC !important}

/* ── Prediction gauges ── */
.gauge-card{background:#FFFFFF;border-radius:14px;padding:20px;text-align:center;border:1px solid rgba(158,98,64,0.08);box-shadow:0 2px 8px rgba(0,0,0,0.04)}
.gauge-label{font-size:0.78rem;color:#8A7A6A;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px}
.gauge-current{font-family:'Space Grotesk';font-size:1.5rem;font-weight:700;color:#CD4631}
.gauge-projected{font-family:'Space Grotesk';font-size:1.5rem;font-weight:700;color:#81ADC8}
.gauge-arrow{font-size:1.1rem;color:#9E6240;margin:4px 0}
.gauge-change{font-size:0.82rem;font-weight:600;color:#4A7C59;background:rgba(74,124,89,0.1);padding:2px 8px;border-radius:10px;display:inline-block}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════
def md_to_html(text: str) -> str:
    """Convert markdown bold/code/lists/tables to HTML, and newlines to <br>."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    lines = text.split("\n")
    html_lines = []
    in_list = False
    in_table = False
    
    for line in lines:
        if line.startswith("- "):
            if not in_list:
                html_lines.append('<ul style="margin-top:8px;margin-bottom:16px;padding-left:24px;">')
                in_list = True
            html_lines.append(f'<li style="margin-bottom:8px;line-height:1.6;">{line[2:]}</li>')
        elif line.startswith("|"):
            if not in_table:
                html_lines.append('<table style="width:100%;border-collapse:collapse;margin:16px 0;background:#FFFFFF;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.05);">')
                in_table = True
            
            if "---" in line:
                continue
                
            cells = [c.strip() for c in line.split("|")[1:-1]]
            row_html = "<tr>"
            
            # If it's the very first row of the table, treat as header
            if len(html_lines) > 0 and html_lines[-1] == '<table style="width:100%;border-collapse:collapse;margin:16px 0;background:#FFFFFF;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.05);">':
                for c in cells:
                    row_html += f'<th style="background:rgba(158,98,64,0.1);color:#9E6240;padding:12px;text-align:left;font-weight:600;border-bottom:2px solid rgba(158,98,64,0.2);">{c}</th>'
            else:
                for c in cells:
                    row_html += f'<td style="padding:12px;border-bottom:1px solid rgba(158,98,64,0.1);color:#4A3A2A;">{c}</td>'
            row_html += "</tr>"
            html_lines.append(row_html)
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_table:
                html_lines.append('</table>')
                in_table = False
                
            if line.strip() == "":
                html_lines.append("<br>")
            else:
                html_lines.append(f"<div style='margin-bottom:8px;'>{line}</div>")
                
    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</table>')
        
    return "".join(html_lines)


def language_selector():
    """Compact language selector showing only 2 non-active options."""
    flags = {"ES": "🇪🇸", "EN": "🇬🇧", "PT": "🇧🇷"}
    active = st.session_state["language"]
    others = [l for l in flags if l != active]
    with st.popover(f"{flags[active]} {active}"):
        for lc in others:
            if st.button(f"{flags[lc]}  {lc}", key=f"lang_{lc}", use_container_width=True):
                st.session_state["language"] = lc
                st.rerun()


def section_insight(key: str):
    """Render a storytelling insight box."""
    st.markdown(f'<div class="insight-box">{md_to_html(t(key))}</div>', unsafe_allow_html=True)


def story_card(icon: str, title: str, body: str):
    """Render a white story card for conclusions."""
    st.markdown(f"""
    <div class="story-card">
        <h3>{icon} {title}</h3>
        <div>{md_to_html(body)}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════
h_col1, h_col2 = st.columns([12, 1])
with h_col1:
    st.markdown(f"""
    <div class="dashboard-header">
        <div>
            <h1>🔄 {t("app_title")}</h1>
            <p>{t("app_subtitle")}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with h_col2:
    language_selector()


# ══════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 24px;">
        <div style="font-size:2.2rem">🔄</div>
        <div style="font-family:'Space Grotesk';font-size:1rem;font-weight:700;color:#DEA47E;">
            {t("sidebar_title")}
        </div>
        <div style="font-size:0.68rem;color:rgba(248,242,220,0.4);margin-top:3px;">
            {t("sidebar_subtitle")}
        </div>
    </div>
    <hr style="border-color:rgba(158,98,64,0.2);margin-bottom:20px;">
    """, unsafe_allow_html=True)

    st.markdown(f"### {t('sidebar_filters')}")
    predictions = load_predictions()
    if predictions is not None and "customer_state" in predictions.columns:
        states = sorted(predictions["customer_state"].dropna().unique().tolist())
        selected_state = st.selectbox(
            t("filter_state"), [t("filter_all_states")] + states, key="filter_state_select",
        )
    else:
        selected_state = t("filter_all_states")

    threshold = st.slider(t("filter_threshold"), 0.0, 1.0, 0.6, 0.05, key="risk_threshold")

    st.markdown(f"""
    <hr style="border-color:rgba(158,98,64,0.2);margin-top:20px;">
    <div style="text-align:center;padding:10px 0;font-size:0.68rem;color:rgba(248,242,220,0.3);">
        {t("sidebar_footer").replace(chr(10),"<br>")}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# LOAD SHARED DATA
# ══════════════════════════════════════════════════
insights = load_insights()
metrics = load_metrics()


# ══════════════════════════════════════════════════
# KPI CARDS ROW (always visible, like reference)
# ══════════════════════════════════════════════════
if insights:
    kpis = insights.get("kpis", {})
    total = kpis.get("total_clientes", 0)
    churn_rate = kpis.get("tasa_churn", 0)
    revenue_risk = kpis.get("revenue_en_riesgo", 0)
    ltv = kpis.get("ltv_promedio", 0)

    rev_display = f"R$ {revenue_risk / 1_000_000:.1f}M" if revenue_risk >= 1_000_000 else f"R$ {revenue_risk:,.0f}"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card kpi-1">
            <div class="kpi-label">{t("kpi_total_customers")}</div>
            <div class="kpi-value">{total:,}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card kpi-2">
            <div class="kpi-label">{t("kpi_churn_rate")}</div>
            <div class="kpi-value">{churn_rate:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card kpi-3">
            <div class="kpi-label">{t("kpi_revenue_at_risk")}</div>
            <div class="kpi-value">{rev_display}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card kpi-4">
            <div class="kpi-label">{t("kpi_avg_ltv")}</div>
            <div class="kpi-value">R$ {ltv:,.0f}</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# INTRO STORYTELLING
# ══════════════════════════════════════════════════
st.markdown("")
st.markdown(f"""
<div class="intro-card">
    <h3>{t("intro_title")}</h3>
    <p>{md_to_html(t("intro_body"))}</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# OVERVIEW INSIGHT
# ══════════════════════════════════════════════════
if insights:
    section_insight("insight_overview")


# ══════════════════════════════════════════════════
# TABS (4 — no Executive Overview, no Model Explainer)
# ══════════════════════════════════════════════════
st.markdown("")
tab1, tab2, tab3, tab4 = st.tabs([
    t("tab_cohort"),
    t("tab_atrisk"),
    t("tab_geo"),
    t("tab_insights"),
])

# ── Cohort Retention ──
with tab1:
    cohort_df = load_cohort_matrix()
    if cohort_df is not None and not cohort_df.empty:
        render_cohort_comparison(insights or {})
        section_insight("insight_cohort")
        render_cohort_heatmap(cohort_df)
        render_retention_curves(cohort_df)
    else:
        st.warning(t("no_data"))

# ── At-Risk Customers (optimized — top priority only) ──
with tab2:
    at_risk = load_at_risk()
    if at_risk is not None and not at_risk.empty:
        section_insight("insight_atrisk")
        render_risk_scatter(at_risk)
        st.markdown("")
        render_risk_table(at_risk)
    else:
        st.warning(t("no_data"))

# ── Geo Intelligence ──
with tab3:
    if insights and "churn_por_estado" in insights:
        section_insight("insight_geo")
        render_churn_map(predictions, insights["churn_por_estado"])
        features_df = load_features()
        if features_df is not None:
            if selected_state != t("filter_all_states") and "customer_state" in features_df.columns:
                features_df = features_df[features_df["customer_state"] == selected_state]
            render_delivery_vs_churn(features_df)
    else:
        st.warning(t("no_data"))

# ── Conclusions ──
with tab4:
    st.markdown(
        f'<h2 style="color:#9E6240;font-family:Space Grotesk;margin-bottom:16px;">'
        f'{t("conclusions_title")}</h2>',
        unsafe_allow_html=True,
    )

    # Causes
    story_card("🔎", t("conclusions_causes_title").replace("🔎 ", ""), t("conclusions_causes"))

    # Key Findings
    story_card("📊", t("conclusions_findings_title").replace("📊 ", ""), t("conclusions_findings"))

    # Recommended Actions
    story_card("🚀", t("conclusions_actions_title").replace("🚀 ", ""), t("conclusions_actions"))

    # Prediction — Visual gauges
    st.markdown(
        f'<h3 style="color:#9E6240;font-family:Space Grotesk;margin:24px 0 12px;">'
        f'{t("conclusions_prediction_title")}</h3>',
        unsafe_allow_html=True,
    )

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown(f"""
        <div class="gauge-card">
            <div class="gauge-label">{t("kpi_churn_rate")}</div>
            <div class="gauge-current">58.9%</div>
            <div class="gauge-arrow">▼</div>
            <div class="gauge-projected">~45%</div>
            <div class="gauge-change">-13.9pp</div>
        </div>""", unsafe_allow_html=True)
    with g2:
        st.markdown("""
        <div class="gauge-card">
            <div class="gauge-label">Revenue Protegido</div>
            <div class="gauge-current">R$ 0</div>
            <div class="gauge-arrow">▲</div>
            <div class="gauge-projected">R$ 3.2M</div>
            <div class="gauge-change">+R$ 3.2M</div>
        </div>""", unsafe_allow_html=True)
    with g3:
        st.markdown("""
        <div class="gauge-card">
            <div class="gauge-label">Retención M+1</div>
            <div class="gauge-current">4.7%</div>
            <div class="gauge-arrow">▲</div>
            <div class="gauge-projected">~12%</div>
            <div class="gauge-change">+7.3pp</div>
        </div>""", unsafe_allow_html=True)
    with g4:
        st.markdown(f"""
        <div class="gauge-card">
            <div class="gauge-label">{t("kpi_avg_ltv")}</div>
            <div class="gauge-current">R$ 165</div>
            <div class="gauge-arrow">▲</div>
            <div class="gauge-projected">R$ 215</div>
            <div class="gauge-change">+30%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        f'<div class="intro-card"><p>{md_to_html(t("conclusions_prediction"))}</p></div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;font-size:0.85rem;color:#8A7A6A;">
    Desarrollado por <strong>Hely Camargo</strong> usando: Python, Streamlit, Scikit-Learn y Plotly.
</div>
""", unsafe_allow_html=True)
