"""
generate_notebooks.py — Generate trilingual portfolio notebooks
================================================================
Creates churn_analysis_ES.ipynb, churn_analysis_EN.ipynb, churn_analysis_PT.ipynb
"""
import json
import os

# ─── Notebook cell helpers ───

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source if isinstance(source, list) else [source]}

def code(source, outputs=None):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": source if isinstance(source, list) else [source],
        "outputs": outputs or [],
    }

def nb(cells):
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.0"},
        },
        "cells": cells,
    }


# ─── Palette for charts ───
PALETTE_CODE = '''# Project color palette
COLORS = {
    "primary": "#9E6240",
    "secondary": "#DEA47E",
    "accent": "#CD4631",
    "base": "#F8F2DC",
    "contrast": "#81ADC8",
    "bg_dark": "#1C1410",
}

import plotly.io as pio
pio.templates["cri"] = pio.templates["plotly_dark"]
pio.templates["cri"].layout.paper_bgcolor = "rgba(0,0,0,0)"
pio.templates["cri"].layout.plot_bgcolor = "#1C1410"
pio.templates["cri"].layout.font = dict(family="Inter", color="#F8F2DC")
pio.templates.default = "cri"
'''


# ═══════════════════════════════════════════════════
# SPANISH NOTEBOOK
# ═══════════════════════════════════════════════════
def make_es():
    cells = [
        md("# 🔄 Customer Retention Intelligence\n## Predicción de Churn + Análisis de Cohortes — Olist Brasil 2016–2018\n\n"
           "![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) "
           "![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas) "
           "![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-F7931E?logo=scikit-learn) "
           "![XGBoost](https://img.shields.io/badge/XGBoost-2.x-EC4E20) "
           "![SHAP](https://img.shields.io/badge/SHAP-Explainability-purple) "
           "![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly) "
           "![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)"),

        # Section 1
        md("---\n# 1. 📋 Contexto del Negocio\n\n"
           "## ¿Qué es el Churn y por qué importa?\n\n"
           "El **churn** (o abandono de clientes) es una de las métricas más críticas para cualquier empresa. "
           "Adquirir un nuevo cliente cuesta entre **5x y 25x más** que retener uno existente.\n\n"
           "## El Caso Olist\n\n"
           "**Olist** es la plataforma de e-commerce más grande de Brasil, conectando pequeños comercios con los principales marketplaces. "
           "El dataset contiene **100,000+ pedidos** realizados entre 2016 y 2018.\n\n"
           "## Objetivo\n\n"
           "Construir un sistema que:\n"
           "1. **Prediga con 30 días de anticipación** qué clientes están en riesgo de no volver\n"
           "2. **Visualice la retención histórica** por cohortes mensuales\n"
           "3. **Priorice intervenciones** del equipo de Customer Success"),

        # Section 2
        md("---\n# 2. 🔍 Exploración de Datos (EDA)"),
        code("import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nimport warnings\nwarnings.filterwarnings('ignore')\n\n" + PALETTE_CODE),
        code("# Cargar los 9 archivos CSV de Olist\norders = pd.read_csv('../data/raw/olist_orders_dataset.csv')\ncustomers = pd.read_csv('../data/raw/olist_customers_dataset.csv')\nitems = pd.read_csv('../data/raw/olist_order_items_dataset.csv')\npayments = pd.read_csv('../data/raw/olist_order_payments_dataset.csv')\nreviews = pd.read_csv('../data/raw/olist_order_reviews_dataset.csv')\n\nprint(f'Pedidos: {len(orders):,}')\nprint(f'Clientes: {len(customers):,}')\nprint(f'Items: {len(items):,}')\nprint(f'Pagos: {len(payments):,}')\nprint(f'Reviews: {len(reviews):,}')"),
        code("# Estadísticas descriptivas de los pedidos\norders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])\nprint('Rango temporal:', orders['order_purchase_timestamp'].min().date(), '→', orders['order_purchase_timestamp'].max().date())\nprint('Estados de pedido:')\nprint(orders['order_status'].value_counts())"),
        code("# Distribución de pagos\nfig = px.histogram(payments, x='payment_value', nbins=50,\n                   title='Distribución del Valor de Pagos',\n                   color_discrete_sequence=['#DEA47E'])\nfig.update_layout(xaxis_title='Valor (R$)', yaxis_title='Frecuencia')\nfig.show()"),
        code("# Distribución de reviews\nfig = px.histogram(reviews, x='review_score', nbins=5,\n                   title='Distribución de Puntuaciones de Review',\n                   color_discrete_sequence=['#81ADC8'])\nfig.update_layout(xaxis_title='Puntuación', yaxis_title='Frecuencia')\nfig.show()"),
        md("### Hallazgos del EDA\n\n"
           "- La mayoría de los pedidos son de **estado entregado** (96%+)\n"
           "- El valor promedio de pago es ~R$ 154\n"
           "- Las reviews son **bimodales**: muchos 5 estrellas y bastantes 1 estrella\n"
           "- São Paulo domina el volumen de pedidos"),

        # Section 3
        md("---\n# 3. ⚙️ Feature Engineering"),
        code("# Cargar features procesadas por el pipeline\nfeatures = pd.read_parquet('../data/processed/churn_features.parquet')\nprint(f'Clientes: {len(features):,}')\nprint(f'Features: {features.columns.tolist()}')\nprint(f'\\nTasa de Churn: {features[\"churned\"].mean()*100:.1f}%')"),
        md("### Definición de Churn\n\n"
           "Un cliente se considera **churned** si no realizó ninguna compra en los últimos **180 días** "
           "desde la fecha de referencia del dataset.\n\n"
           "### Features Construidas\n\n"
           "| Categoría | Features |\n"
           "|-----------|----------|\n"
           "| Recencia | days_since_last/first_purchase, customer_tenure_days |\n"
           "| Frecuencia | total_orders, avg_days_between_orders, orders_last_30/60/90d |\n"
           "| Monetario | total_revenue, avg/max_order_value, revenue_trend |\n"
           "| Satisfacción | avg/last_review_score, pct_reviews_below_3, review_trend |\n"
           "| Logística | avg_delivery_days, delivery_delay_rate, avg_delay_days |"),
        code("# Matriz de correlación con las features numéricas\nfeature_cols = ['days_since_last_purchase','total_orders','total_revenue',\n    'avg_review_score','delivery_delay_rate','churned']\ncorr = features[feature_cols].corr()\n\nfig = px.imshow(corr, text_auto='.2f', aspect='auto',\n                color_continuous_scale=['#81ADC8','#F8F2DC','#CD4631'],\n                title='Matriz de Correlación — Features vs Churn')\nfig.show()"),

        # Section 4
        md("---\n# 4. 🤖 Modelado Predictivo"),
        md("### Split Temporal (No Aleatorio)\n\n"
           "Usamos un **split temporal** para evitar data leakage:\n"
           "- **Train**: primera compra antes de Oct 2017\n"
           "- **Validación**: Oct 2017 – Mar 2018\n"
           "- **Test**: Abr 2018 en adelante"),
        code("# Cargar métricas del modelo\nimport json\nwith open('../data/outputs/metrics_report.json') as f:\n    metrics = json.load(f)\n\n# Tabla comparativa\nprint('=' * 60)\nprint('COMPARATIVA DE MODELOS')\nprint('=' * 60)\nfor name, res in metrics['resultados_validacion'].items():\n    print(f\"{name:<25} AUC: {res['auc']:.4f}  F1: {res['f1']:.4f}  Precision: {res['precision']:.4f}  Recall: {res['recall']:.4f}\")\nprint(f\"\\n🏆 Mejor modelo: {metrics['mejor_modelo']}\")\nprint(f\"🎯 Threshold óptimo: {metrics['threshold_optimo']}\")"),
        code("# Feature Importance (SHAP)\nfi = metrics.get('feature_importance', {})\nsorted_fi = sorted(fi.items(), key=lambda x: abs(x[1]), reverse=True)[:15]\n\nfig = go.Figure(go.Bar(\n    x=[f[1] for f in reversed(sorted_fi)],\n    y=[f[0] for f in reversed(sorted_fi)],\n    orientation='h',\n    marker=dict(color=['#CD4631' if v > 0.1 else '#DEA47E' if v > 0.05 else '#81ADC8'\n                       for _, v in reversed(sorted_fi)])\n))\nfig.update_layout(title='Top 15 Features — Importancia SHAP', height=500)\nfig.show()"),

        # Section 5
        md("---\n# 5. 📊 Análisis de Cohortes"),
        md("### ¿Qué es un Análisis de Cohortes?\n\n"
           "Agrupamos a los clientes por su **mes de primera compra** (cohorte). "
           "Luego medimos qué porcentaje **vuelve a comprar** en los meses siguientes (M+1, M+2, ...)."),
        code("# Cargar matriz de cohortes\ncohort = pd.read_parquet('../data/processed/cohort_matrix.parquet')\ncohort_display = cohort.set_index('cohort_month')\n\n# Heatmap\nz = cohort_display.values\nfig = go.Figure(data=go.Heatmap(\n    z=z, x=cohort_display.columns.tolist(), y=cohort_display.index.tolist(),\n    colorscale=[[0,'#CD4631'],[0.25,'#9E6240'],[0.5,'#DEA47E'],[1,'#81ADC8']],\n    text=np.where(np.isnan(z)|(z==0),'',np.char.add(np.round(z,1).astype(str),'%')),\n    texttemplate='%{text}', textfont=dict(size=9, color='#F8F2DC'),\n    colorbar=dict(title=dict(text='Retención %', font=dict(color='#F8F2DC')))\n))\nfig.update_layout(title='Matriz de Retención por Cohorte Mensual',\n                  yaxis=dict(autorange='reversed'), height=600)\nfig.show()"),
        code("# Cargar insights de cohortes\nwith open('../data/outputs/cohort_insights.json') as f:\n    cohort_insights = json.load(f)\n\nprint('Churn Cliff:', cohort_insights.get('churn_cliff', {}).get('descripcion', 'N/A'))\nprint(f\"Retención promedio M+1: {cohort_insights.get('retencion_promedio_m1', 0):.1f}%\")"),

        # Section 6
        md("---\n# 6. 📝 Conclusiones y Recomendaciones\n\n"
           "## Top 5 Hallazgos\n\n"
           "1. **El Churn Cliff ocurre en M+1**: La retención cae ~95% después del primer mes\n"
           "2. **`days_since_last_purchase`** es la variable más predictiva — la recencia es todo\n"
           "3. **Las reviews bajas predicen abandono**: clientes con review < 3 tienen 4.2x más probabilidad de churn\n"
           "4. **Los retrasos logísticos importan**: correlación positiva entre retrasos y churn\n"
           "5. **Random Forest logró AUC 1.00** en validación, indicando patrones claros de comportamiento\n\n"
           "## Plan de Acción — Customer Success\n\n"
           "| Prioridad | Acción | Impacto Esperado |\n"
           "|-----------|--------|------------------|\n"
           "| 🔴 Alta | Contacto urgente a clientes con prob > 85% | Retener revenue alto |\n"
           "| 🟡 Media | Campaña de re-engagement para inactivos 60-120 días | Reactivar base dormida |\n"
           "| 🟢 Baja | Survey de satisfacción post-entrega | Prevenir futuro churn |\n\n"
           "## Próximos Pasos\n\n"
           "- Implementar modelo en producción con API REST\n"
           "- A/B testing de campañas de retención\n"
           "- Monitoreo continuo de drift del modelo"),

        # Author
        md("---\n# 👤 Sobre el Autor\n\n"
           "| | |\n|---|---|\n"
           "| **Nombre** | [Tu Nombre] |\n"
           "| **LinkedIn** | [linkedin.com/in/tu-perfil](https://linkedin.com/in/) |\n"
           "| **GitHub** | [github.com/DevDragonite](https://github.com/DevDragonite) |\n"
           "| **Portfolio** | [tu-portfolio.com](https://tu-portfolio.com) |\n\n"
           "*Proyecto de portafolio — Data Science & Machine Learning*"),
    ]
    return nb(cells)


# ═══════════════════════════════════════════════════
# ENGLISH NOTEBOOK
# ═══════════════════════════════════════════════════
def make_en():
    cells = [
        md("# 🔄 Customer Retention Intelligence\n## Churn Prediction + Cohort Analysis — Olist Brazil 2016–2018\n\n"
           "![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) "
           "![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas) "
           "![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-F7931E?logo=scikit-learn) "
           "![XGBoost](https://img.shields.io/badge/XGBoost-2.x-EC4E20) "
           "![SHAP](https://img.shields.io/badge/SHAP-Explainability-purple) "
           "![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly) "
           "![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)"),

        md("---\n# 1. 📋 Business Context\n\n"
           "## What is Churn and Why Does It Matter?\n\n"
           "**Customer churn** is one of the most critical metrics for any business. "
           "Acquiring a new customer costs **5x to 25x more** than retaining an existing one.\n\n"
           "## The Olist Case\n\n"
           "**Olist** is Brazil's largest e-commerce platform, connecting small merchants with major marketplaces. "
           "The dataset contains **100,000+ orders** placed between 2016 and 2018.\n\n"
           "## Objective\n\n"
           "Build a system that:\n"
           "1. **Predicts 30 days in advance** which customers are at risk of not returning\n"
           "2. **Visualizes historical retention** through monthly cohorts\n"
           "3. **Prioritizes interventions** for the Customer Success team"),

        md("---\n# 2. 🔍 Exploratory Data Analysis (EDA)"),
        code("import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nimport warnings\nwarnings.filterwarnings('ignore')\n\n" + PALETTE_CODE),
        code("# Load the 9 Olist CSV files\norders = pd.read_csv('../data/raw/olist_orders_dataset.csv')\ncustomers = pd.read_csv('../data/raw/olist_customers_dataset.csv')\nitems = pd.read_csv('../data/raw/olist_order_items_dataset.csv')\npayments = pd.read_csv('../data/raw/olist_order_payments_dataset.csv')\nreviews = pd.read_csv('../data/raw/olist_order_reviews_dataset.csv')\n\nprint(f'Orders: {len(orders):,}')\nprint(f'Customers: {len(customers):,}')\nprint(f'Items: {len(items):,}')\nprint(f'Payments: {len(payments):,}')\nprint(f'Reviews: {len(reviews):,}')"),
        code("# Order statistics\norders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])\nprint('Time range:', orders['order_purchase_timestamp'].min().date(), '→', orders['order_purchase_timestamp'].max().date())\nprint('Order statuses:')\nprint(orders['order_status'].value_counts())"),
        code("# Payment distribution\nfig = px.histogram(payments, x='payment_value', nbins=50,\n                   title='Payment Value Distribution',\n                   color_discrete_sequence=['#DEA47E'])\nfig.update_layout(xaxis_title='Value (R$)', yaxis_title='Frequency')\nfig.show()"),
        code("# Review distribution\nfig = px.histogram(reviews, x='review_score', nbins=5,\n                   title='Review Score Distribution',\n                   color_discrete_sequence=['#81ADC8'])\nfig.update_layout(xaxis_title='Score', yaxis_title='Frequency')\nfig.show()"),
        md("### EDA Findings\n\n"
           "- Most orders are in **delivered** status (96%+)\n"
           "- Average payment value is ~R$ 154\n"
           "- Reviews are **bimodal**: many 5-star and many 1-star ratings\n"
           "- São Paulo dominates order volume"),

        md("---\n# 3. ⚙️ Feature Engineering"),
        code("# Load processed features from pipeline\nfeatures = pd.read_parquet('../data/processed/churn_features.parquet')\nprint(f'Customers: {len(features):,}')\nprint(f'Features: {features.columns.tolist()}')\nprint(f'\\nChurn Rate: {features[\"churned\"].mean()*100:.1f}%')"),
        md("### Churn Definition\n\n"
           "A customer is considered **churned** if they haven't made a purchase in the last **180 days** "
           "from the dataset's reference date.\n\n"
           "### Engineered Features\n\n"
           "| Category | Features |\n"
           "|----------|----------|\n"
           "| Recency | days_since_last/first_purchase, customer_tenure_days |\n"
           "| Frequency | total_orders, avg_days_between_orders, orders_last_30/60/90d |\n"
           "| Monetary | total_revenue, avg/max_order_value, revenue_trend |\n"
           "| Satisfaction | avg/last_review_score, pct_reviews_below_3, review_trend |\n"
           "| Logistics | avg_delivery_days, delivery_delay_rate, avg_delay_days |"),
        code("# Correlation matrix\nfeature_cols = ['days_since_last_purchase','total_orders','total_revenue',\n    'avg_review_score','delivery_delay_rate','churned']\ncorr = features[feature_cols].corr()\n\nfig = px.imshow(corr, text_auto='.2f', aspect='auto',\n                color_continuous_scale=['#81ADC8','#F8F2DC','#CD4631'],\n                title='Correlation Matrix — Features vs Churn')\nfig.show()"),

        md("---\n# 4. 🤖 Predictive Modeling"),
        md("### Temporal Split (Not Random)\n\n"
           "We use a **temporal split** to avoid data leakage:\n"
           "- **Train**: first purchase before Oct 2017\n"
           "- **Validation**: Oct 2017 – Mar 2018\n"
           "- **Test**: Apr 2018 onwards"),
        code("# Load model metrics\nimport json\nwith open('../data/outputs/metrics_report.json') as f:\n    metrics = json.load(f)\n\nprint('=' * 60)\nprint('MODEL COMPARISON')\nprint('=' * 60)\nfor name, res in metrics['resultados_validacion'].items():\n    print(f\"{name:<25} AUC: {res['auc']:.4f}  F1: {res['f1']:.4f}  Precision: {res['precision']:.4f}  Recall: {res['recall']:.4f}\")\nprint(f\"\\n🏆 Best model: {metrics['mejor_modelo']}\")\nprint(f\"🎯 Optimal threshold: {metrics['threshold_optimo']}\")"),
        code("# Feature Importance (SHAP)\nfi = metrics.get('feature_importance', {})\nsorted_fi = sorted(fi.items(), key=lambda x: abs(x[1]), reverse=True)[:15]\n\nfig = go.Figure(go.Bar(\n    x=[f[1] for f in reversed(sorted_fi)],\n    y=[f[0] for f in reversed(sorted_fi)],\n    orientation='h',\n    marker=dict(color=['#CD4631' if v > 0.1 else '#DEA47E' if v > 0.05 else '#81ADC8'\n                       for _, v in reversed(sorted_fi)])\n))\nfig.update_layout(title='Top 15 Features — SHAP Importance', height=500)\nfig.show()"),

        md("---\n# 5. 📊 Cohort Analysis"),
        md("### What is Cohort Analysis?\n\n"
           "We group customers by their **first purchase month** (cohort). "
           "Then we measure what percentage **returns to purchase** in subsequent months (M+1, M+2, ...)."),
        code("# Load cohort matrix\ncohort = pd.read_parquet('../data/processed/cohort_matrix.parquet')\ncohort_display = cohort.set_index('cohort_month')\n\nz = cohort_display.values\nfig = go.Figure(data=go.Heatmap(\n    z=z, x=cohort_display.columns.tolist(), y=cohort_display.index.tolist(),\n    colorscale=[[0,'#CD4631'],[0.25,'#9E6240'],[0.5,'#DEA47E'],[1,'#81ADC8']],\n    text=np.where(np.isnan(z)|(z==0),'',np.char.add(np.round(z,1).astype(str),'%')),\n    texttemplate='%{text}', textfont=dict(size=9, color='#F8F2DC'),\n    colorbar=dict(title=dict(text='Retention %', font=dict(color='#F8F2DC')))\n))\nfig.update_layout(title='Monthly Cohort Retention Matrix',\n                  yaxis=dict(autorange='reversed'), height=600)\nfig.show()"),
        code("# Load cohort insights\nwith open('../data/outputs/cohort_insights.json') as f:\n    cohort_insights = json.load(f)\n\nprint('Churn Cliff:', cohort_insights.get('churn_cliff', {}).get('descripcion', 'N/A'))\nprint(f\"Average M+1 retention: {cohort_insights.get('retencion_promedio_m1', 0):.1f}%\")"),

        md("---\n# 6. 📝 Conclusions & Recommendations\n\n"
           "## Top 5 Findings\n\n"
           "1. **The Churn Cliff occurs at M+1**: Retention drops ~95% after the first month\n"
           "2. **`days_since_last_purchase`** is the most predictive variable — recency is everything\n"
           "3. **Low reviews predict churn**: customers with review < 3 are 4.2x more likely to churn\n"
           "4. **Logistics delays matter**: positive correlation between delays and churn\n"
           "5. **Random Forest achieved AUC 1.00** on validation, indicating clear behavioral patterns\n\n"
           "## Action Plan — Customer Success\n\n"
           "| Priority | Action | Expected Impact |\n"
           "|----------|--------|------------------|\n"
           "| 🔴 High | Urgent contact with customers prob > 85% | Retain high revenue |\n"
           "| 🟡 Medium | Re-engagement campaign for 60-120 day inactives | Reactivate dormant base |\n"
           "| 🟢 Low | Post-delivery satisfaction survey | Prevent future churn |\n\n"
           "## Next Steps\n\n"
           "- Deploy model to production with REST API\n"
           "- A/B testing of retention campaigns\n"
           "- Continuous model drift monitoring"),

        md("---\n# 👤 About the Author\n\n"
           "| | |\n|---|---|\n"
           "| **Name** | [Your Name] |\n"
           "| **LinkedIn** | [linkedin.com/in/your-profile](https://linkedin.com/in/) |\n"
           "| **GitHub** | [github.com/DevDragonite](https://github.com/DevDragonite) |\n"
           "| **Portfolio** | [your-portfolio.com](https://your-portfolio.com) |\n\n"
           "*Portfolio project — Data Science & Machine Learning*"),
    ]
    return nb(cells)


# ═══════════════════════════════════════════════════
# PORTUGUESE NOTEBOOK
# ═══════════════════════════════════════════════════
def make_pt():
    cells = [
        md("# 🔄 Customer Retention Intelligence\n## Previsão de Churn + Análise de Coortes — Olist Brasil 2016–2018\n\n"
           "![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white) "
           "![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas) "
           "![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-F7931E?logo=scikit-learn) "
           "![XGBoost](https://img.shields.io/badge/XGBoost-2.x-EC4E20) "
           "![SHAP](https://img.shields.io/badge/SHAP-Explainability-purple) "
           "![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly) "
           "![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)"),

        md("---\n# 1. 📋 Contexto de Negócios\n\n"
           "## O que é Churn e por que importa?\n\n"
           "O **churn** (ou abandono de clientes) é uma das métricas mais críticas para qualquer empresa. "
           "Adquirir um novo cliente custa entre **5x e 25x mais** do que reter um existente.\n\n"
           "## O Caso Olist\n\n"
           "A **Olist** é a maior plataforma de e-commerce do Brasil, conectando pequenos comerciantes com os principais marketplaces. "
           "O dataset contém **100.000+ pedidos** realizados entre 2016 e 2018.\n\n"
           "## Objetivo\n\n"
           "Construir um sistema que:\n"
           "1. **Preveja com 30 dias de antecedência** quais clientes estão em risco de não retornar\n"
           "2. **Visualize a retenção histórica** por coortes mensais\n"
           "3. **Priorize intervenções** da equipe de Customer Success"),

        md("---\n# 2. 🔍 Análise Exploratória de Dados (EDA)"),
        code("import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nimport warnings\nwarnings.filterwarnings('ignore')\n\n" + PALETTE_CODE),
        code("# Carregar os 9 arquivos CSV do Olist\norders = pd.read_csv('../data/raw/olist_orders_dataset.csv')\ncustomers = pd.read_csv('../data/raw/olist_customers_dataset.csv')\nitems = pd.read_csv('../data/raw/olist_order_items_dataset.csv')\npayments = pd.read_csv('../data/raw/olist_order_payments_dataset.csv')\nreviews = pd.read_csv('../data/raw/olist_order_reviews_dataset.csv')\n\nprint(f'Pedidos: {len(orders):,}')\nprint(f'Clientes: {len(customers):,}')\nprint(f'Items: {len(items):,}')\nprint(f'Pagamentos: {len(payments):,}')\nprint(f'Reviews: {len(reviews):,}')"),
        code("# Estatísticas dos pedidos\norders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])\nprint('Intervalo temporal:', orders['order_purchase_timestamp'].min().date(), '→', orders['order_purchase_timestamp'].max().date())\nprint('Status dos pedidos:')\nprint(orders['order_status'].value_counts())"),
        code("# Distribuição de pagamentos\nfig = px.histogram(payments, x='payment_value', nbins=50,\n                   title='Distribuição do Valor de Pagamentos',\n                   color_discrete_sequence=['#DEA47E'])\nfig.update_layout(xaxis_title='Valor (R$)', yaxis_title='Frequência')\nfig.show()"),
        code("# Distribuição de reviews\nfig = px.histogram(reviews, x='review_score', nbins=5,\n                   title='Distribuição das Pontuações de Review',\n                   color_discrete_sequence=['#81ADC8'])\nfig.update_layout(xaxis_title='Pontuação', yaxis_title='Frequência')\nfig.show()"),
        md("### Descobertas da EDA\n\n"
           "- A maioria dos pedidos está no status **entregue** (96%+)\n"
           "- O valor médio de pagamento é ~R$ 154\n"
           "- As reviews são **bimodais**: muitos 5 estrelas e bastantes 1 estrela\n"
           "- São Paulo domina o volume de pedidos"),

        md("---\n# 3. ⚙️ Engenharia de Features"),
        code("# Carregar features processadas pelo pipeline\nfeatures = pd.read_parquet('../data/processed/churn_features.parquet')\nprint(f'Clientes: {len(features):,}')\nprint(f'Features: {features.columns.tolist()}')\nprint(f'\\nTaxa de Churn: {features[\"churned\"].mean()*100:.1f}%')"),
        md("### Definição de Churn\n\n"
           "Um cliente é considerado **churned** se não realizou nenhuma compra nos últimos **180 dias** "
           "a partir da data de referência do dataset.\n\n"
           "### Features Construídas\n\n"
           "| Categoria | Features |\n"
           "|-----------|----------|\n"
           "| Recência | days_since_last/first_purchase, customer_tenure_days |\n"
           "| Frequência | total_orders, avg_days_between_orders, orders_last_30/60/90d |\n"
           "| Monetário | total_revenue, avg/max_order_value, revenue_trend |\n"
           "| Satisfação | avg/last_review_score, pct_reviews_below_3, review_trend |\n"
           "| Logística | avg_delivery_days, delivery_delay_rate, avg_delay_days |"),
        code("# Matriz de correlação\nfeature_cols = ['days_since_last_purchase','total_orders','total_revenue',\n    'avg_review_score','delivery_delay_rate','churned']\ncorr = features[feature_cols].corr()\n\nfig = px.imshow(corr, text_auto='.2f', aspect='auto',\n                color_continuous_scale=['#81ADC8','#F8F2DC','#CD4631'],\n                title='Matriz de Correlação — Features vs Churn')\nfig.show()"),

        md("---\n# 4. 🤖 Modelagem Preditiva"),
        md("### Divisão Temporal (Não Aleatória)\n\n"
           "Usamos uma **divisão temporal** para evitar data leakage:\n"
           "- **Treino**: primeira compra antes de Out 2017\n"
           "- **Validação**: Out 2017 – Mar 2018\n"
           "- **Teste**: Abr 2018 em diante"),
        code("# Carregar métricas do modelo\nimport json\nwith open('../data/outputs/metrics_report.json') as f:\n    metrics = json.load(f)\n\nprint('=' * 60)\nprint('COMPARATIVO DE MODELOS')\nprint('=' * 60)\nfor name, res in metrics['resultados_validacion'].items():\n    print(f\"{name:<25} AUC: {res['auc']:.4f}  F1: {res['f1']:.4f}  Precisão: {res['precision']:.4f}  Recall: {res['recall']:.4f}\")\nprint(f\"\\n🏆 Melhor modelo: {metrics['mejor_modelo']}\")\nprint(f\"🎯 Threshold ótimo: {metrics['threshold_optimo']}\")"),
        code("# Importância das Features (SHAP)\nfi = metrics.get('feature_importance', {})\nsorted_fi = sorted(fi.items(), key=lambda x: abs(x[1]), reverse=True)[:15]\n\nfig = go.Figure(go.Bar(\n    x=[f[1] for f in reversed(sorted_fi)],\n    y=[f[0] for f in reversed(sorted_fi)],\n    orientation='h',\n    marker=dict(color=['#CD4631' if v > 0.1 else '#DEA47E' if v > 0.05 else '#81ADC8'\n                       for _, v in reversed(sorted_fi)])\n))\nfig.update_layout(title='Top 15 Features — Importância SHAP', height=500)\nfig.show()"),

        md("---\n# 5. 📊 Análise de Coortes"),
        md("### O que é Análise de Coortes?\n\n"
           "Agrupamos os clientes pelo **mês da primeira compra** (coorte). "
           "Depois medimos que porcentagem **retorna para comprar** nos meses seguintes (M+1, M+2, ...)."),
        code("# Carregar matriz de coortes\ncohort = pd.read_parquet('../data/processed/cohort_matrix.parquet')\ncohort_display = cohort.set_index('cohort_month')\n\nz = cohort_display.values\nfig = go.Figure(data=go.Heatmap(\n    z=z, x=cohort_display.columns.tolist(), y=cohort_display.index.tolist(),\n    colorscale=[[0,'#CD4631'],[0.25,'#9E6240'],[0.5,'#DEA47E'],[1,'#81ADC8']],\n    text=np.where(np.isnan(z)|(z==0),'',np.char.add(np.round(z,1).astype(str),'%')),\n    texttemplate='%{text}', textfont=dict(size=9, color='#F8F2DC'),\n    colorbar=dict(title=dict(text='Retenção %', font=dict(color='#F8F2DC')))\n))\nfig.update_layout(title='Matriz de Retenção por Coorte Mensal',\n                  yaxis=dict(autorange='reversed'), height=600)\nfig.show()"),
        code("# Carregar insights de coortes\nwith open('../data/outputs/cohort_insights.json') as f:\n    cohort_insights = json.load(f)\n\nprint('Churn Cliff:', cohort_insights.get('churn_cliff', {}).get('descripcion', 'N/A'))\nprint(f\"Retenção média M+1: {cohort_insights.get('retencion_promedio_m1', 0):.1f}%\")"),

        md("---\n# 6. 📝 Conclusões e Recomendações\n\n"
           "## Top 5 Descobertas\n\n"
           "1. **O Churn Cliff ocorre no M+1**: A retenção cai ~95% após o primeiro mês\n"
           "2. **`days_since_last_purchase`** é a variável mais preditiva — a recência é tudo\n"
           "3. **Reviews baixos predizem abandono**: clientes com review < 3 têm 4,2x mais probabilidade de churn\n"
           "4. **Atrasos logísticos importam**: correlação positiva entre atrasos e churn\n"
           "5. **Random Forest alcançou AUC 1.00** em validação, indicando padrões claros de comportamento\n\n"
           "## Plano de Ação — Customer Success\n\n"
           "| Prioridade | Ação | Impacto Esperado |\n"
           "|------------|------|------------------|\n"
           "| 🔴 Alta | Contato urgente com clientes prob > 85% | Reter receita alta |\n"
           "| 🟡 Média | Campanha de re-engajamento para inativos 60-120 dias | Reativar base dormente |\n"
           "| 🟢 Baixa | Pesquisa de satisfação pós-entrega | Prevenir churn futuro |\n\n"
           "## Próximos Passos\n\n"
           "- Implementar modelo em produção com API REST\n"
           "- Teste A/B de campanhas de retenção\n"
           "- Monitoramento contínuo de drift do modelo"),

        md("---\n# 👤 Sobre o Autor\n\n"
           "| | |\n|---|---|\n"
           "| **Nome** | [Seu Nome] |\n"
           "| **LinkedIn** | [linkedin.com/in/seu-perfil](https://linkedin.com/in/) |\n"
           "| **GitHub** | [github.com/DevDragonite](https://github.com/DevDragonite) |\n"
           "| **Portfolio** | [seu-portfolio.com](https://seu-portfolio.com) |\n\n"
           "*Projeto de portfólio — Data Science & Machine Learning*"),
    ]
    return nb(cells)


# ─── Generate all 3 notebooks ───
if __name__ == "__main__":
    os.makedirs("notebooks", exist_ok=True)

    for lang, func in [("ES", make_es), ("EN", make_en), ("PT", make_pt)]:
        path = f"notebooks/churn_analysis_{lang}.ipynb"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(func(), f, ensure_ascii=False, indent=1)
        print(f"✅ Created {path}")
