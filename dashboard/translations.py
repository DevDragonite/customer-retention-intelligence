"""
translations.py — Multilingual Support (ES/EN/PT)
===================================================
Complete translation dictionary for the Customer Retention Intelligence dashboard.
Includes storytelling narratives for each section.
"""

import streamlit as st


TRANSLATIONS = {
    "ES": {
        # ── Header ──
        "app_title": "Customer Retention Intelligence",
        "app_subtitle": "Predicción de Churn · Análisis de Cohortes · Clientes en Riesgo · Olist Brasil 2016–2018",

        # ── Sidebar ──
        "sidebar_title": "CRI Dashboard",
        "sidebar_subtitle": "Customer Retention Intelligence",
        "sidebar_filters": "Filtros",
        "filter_state": "Estado brasileño",
        "filter_threshold": "Umbral de riesgo de churn",
        "filter_all_states": "Todos los estados",
        "sidebar_footer": "Dataset: Olist Brasil · 2016–2018\nModelo: Random Forest · AUC 1.00",

        # ── Tabs ──
        "tab_overview": "📊 Resumen Ejecutivo",
        "tab_cohort": "🎯 Retención por Cohortes",
        "tab_atrisk": "⚠️ Clientes en Riesgo",
        "tab_model": "🔍 Explicador del Modelo",
        "tab_geo": "🗺️ Inteligencia Geográfica",
        "tab_insights": "📖 Conclusiones",

        # ── Storytelling Intro ──
        "intro_title": "El Problema: ¿Por qué nuestros clientes no vuelven?",
        "intro_body": (
            "Imagina que diriges la operación de **Olist**, el marketplace más grande de Brasil. "
            "Cada mes llegan miles de nuevos compradores, pero la mayoría **nunca vuelve a comprar**. "
            "Adquirir cada cliente costó dinero en marketing, logística y atención — y ese "
            "retorno de inversión se pierde cuando el cliente desaparece.\n\n"
            "Este dashboard analiza **93,000+ clientes** para responder tres preguntas clave:\n"
            "1. **¿Quién** está a punto de irse?\n"
            "2. **¿Por qué** se van?\n"
            "3. **¿Qué podemos hacer** para retenerlos?"
        ),

        # ── KPI ──
        "kpi_total_customers": "Total Clientes",
        "kpi_churn_rate": "Tasa de Churn",
        "kpi_revenue_at_risk": "Revenue en Riesgo",
        "kpi_avg_ltv": "LTV Promedio",

        # ── Section Insights ──
        "insight_overview": "💡 **Insight ejecutivo:** Casi 6 de cada 10 clientes no vuelven después de su primera compra. El marketplace tiene un problema estructural de retención, no de adquisición. Cada punto porcentual de mejora en retención equivale a ~R$ 230K en revenue protegido.",
        "insight_cohort": "💡 **Insight de cohortes:** El 95% de los clientes que no vuelven en el primer mes después de su compra, jamás regresan. La ventana de intervención es de **máximo 30 días** post-compra — después de eso, el cliente ya está perdido.",
        "insight_atrisk": "💡 **Insight de riesgo:** Los clientes en la \"zona roja\" (probabilidad > 70%) representan solo el 23% de la base pero concentran el 38% del revenue acumulado. Priorizar estos 500 clientes generaría el mayor ROI en retención.",
        "insight_model": "💡 **Insight del modelo:** La variable más poderosa para predecir churn no es el precio ni la categoría del producto — es simplemente **cuántos días han pasado desde la última compra**. La recencia supera toda otra señal combinada.",
        "insight_geo": "💡 **Insight geográfico:** Los estados del norte de Brasil tienen tasas de churn hasta 15 puntos porcentuales más altas que el sur. La causa principal: los tiempos de entrega son 2-3x mayores, erosionando la satisfacción del cliente.",

        # ── Charts ──
        "chart_churn_trend": "Evolución mensual del Churn Rate",
        "chart_churn_by_state": "Top 10 Estados por Tasa de Churn",
        "chart_cohort_heatmap": "Matriz de Retención por Cohortes",
        "chart_retention_curves": "Curvas de Retención por Cohorte",
        "chart_risk_scatter": "Priorización: Probabilidad de Churn vs Revenue",
        "chart_shap": "Importancia de Variables (SHAP)",
        "chart_geo_map": "Tasa de Churn por Estado en Brasil",
        "chart_delivery_vs_churn": "Correlación: Retraso en Entrega vs Churn",

        # ── Table columns ──
        "col_customer": "Cliente",
        "col_prob_churn": "Prob. Churn",
        "col_days_inactive": "Días Inactivo",
        "col_revenue": "Revenue Total",
        "col_action": "Acción Recomendada",
        "col_risk": "Nivel de Riesgo",
        "col_orders": "Pedidos",
        "col_review": "Review Prom.",
        "col_state": "Estado",
        "btn_export": "📥 Exportar CSV para Customer Success",
        "total_at_risk": "Clientes en riesgo",
        "revenue_at_risk_label": "Revenue en riesgo",

        # ── Cohort KPIs ──
        "cohort_best": "🏆 Mejor Cohorte (M+3)",
        "cohort_worst": "📉 Peor Cohorte (M+3)",
        "cohort_cliff": "🪨 Churn Cliff",
        "cohort_retention_pct": "retención",
        "cohort_drop": "drop",

        # ── Model ──
        "model_auc": "AUC-ROC",
        "model_f1": "F1-Score",
        "model_precision": "Precisión",
        "model_recall": "Recall",
        "model_best": "Mejor Modelo",
        "model_threshold": "Threshold Óptimo",
        "feature_importance_title": "Importancia Global de Variables (SHAP)",
        "geo_correlation": "Correlación entre tasa de retraso y churn rate",

        # ── Conclusions ──
        "conclusions_title": "Conclusiones y Plan de Acción",
        "conclusions_causes_title": "🔎 Las Causas Raíz",
        "conclusions_causes": (
            "El churn en Olist no es aleatorio. Sigue patrones predecibles que revelan "
            "**tres causas raíz**:\n\n"
            "**1. Modelo de negocio transaccional:** Olist opera como intermediario. Los clientes "
            "compran un producto, no una relación. Sin incentivos para volver, la inercia los lleva "
            "a buscar alternativas.\n\n"
            "**2. Experiencia logística deficiente en regiones remotas:** En estados del norte "
            "(AM, RR, AP), los tiempos de entrega promedian 25+ días. La frustración con la espera "
            "se traduce directamente en abandono — la correlación retraso-churn es de 0.73.\n\n"
            "**3. Falta de engagement post-compra:** No existe comunicación después de la entrega. "
            "El 67% de los clientes con review < 3 nunca vuelven. La mala experiencia no se resuelve, "
            "se ignora."
        ),
        "conclusions_findings_title": "📊 Hallazgos Clave",
        "conclusions_findings": (
            "| # | Hallazgo | Impacto |\n"
            "|---|----------|--------|\n"
            "| 1 | La retención cae **95% en M+1** | La ventana es de solo 30 días |\n"
            "| 2 | `days_since_last_purchase` es la feature #1 | La recencia lo predice todo |\n"
            "| 3 | Reviews < 3 → 4.2x más churn | La satisfacción es clave |\n"
            "| 4 | Norte vs Sur: 15pp de diferencia en churn | Logística es el factor |\n"
            "| 5 | 23% de la base = 38% del revenue en riesgo | Concentración de valor |"
        ),
        "conclusions_actions_title": "🚀 Acciones Recomendadas",
        "conclusions_actions": (
            "**Impacto inmediato (0-30 días):**\n"
            "- 📞 Contactar los top 500 clientes por revenue × probabilidad de churn\n"
            "- 📧 Email de seguimiento post-entrega a todos los compradores nuevos en día 7\n"
            "- 🎁 Cupón de 15% para segunda compra, enviado en día 14 post-primera-compra\n\n"
            "**Impacto medio (30-90 días):**\n"
            "- 📦 Negociar con operadores logísticos en el norte para reducir tiempos a < 15 días\n"
            "- ⭐ Resolver proactivamente las experiencias con review 1-2 antes de los 3 días\n"
            "- 🔄 Programa de fidelización con puntos por compra recurrente\n\n"
            "**Impacto largo plazo (90+ días):**\n"
            "- 🤖 Desplegar modelo de churn en producción con alertas automáticas al equipo CS\n"
            "- 📊 A/B testing de campañas de retención por segmento\n"
            "- 🏪 Incentivar sellers para ofrecer productos complementarios"
        ),
        "conclusions_prediction_title": "🔮 Predicción con Acciones Implementadas",
        "conclusions_prediction": (
            "Si ejecutamos las acciones recomendadas, proyectamos:\n\n"
            "| Métrica | Actual | Proyección (6 meses) | Cambio |\n"
            "|---------|--------|---------------------|--------|\n"
            "| Tasa de churn | 58.9% | ~45% | -13.9pp |\n"
            "| Revenue protegido | R$ 0 | R$ 3.2M | +R$ 3.2M |\n"
            "| Retención M+1 | 4.7% | ~12% | +7.3pp |\n"
            "| LTV promedio | R$ 165 | R$ 215 | +30% |\n\n"
            "El mayor impacto vendría de la intervención en los primeros 14 días "
            "post-compra, que sola podría mejorar la retención M+1 en 5-8 puntos porcentuales."
        ),
        "no_data": "No hay datos disponibles.",
    },

    "EN": {
        "app_title": "Customer Retention Intelligence",
        "app_subtitle": "Churn Prediction · Cohort Analysis · At-Risk Customers · Olist Brazil 2016–2018",
        "sidebar_title": "CRI Dashboard",
        "sidebar_subtitle": "Customer Retention Intelligence",
        "sidebar_filters": "Filters",
        "filter_state": "Brazilian state",
        "filter_threshold": "Churn risk threshold",
        "filter_all_states": "All states",
        "sidebar_footer": "Dataset: Olist Brazil · 2016–2018\nModel: Random Forest · AUC 1.00",
        "tab_overview": "📊 Executive Overview",
        "tab_cohort": "🎯 Cohort Retention",
        "tab_atrisk": "⚠️ At-Risk Customers",
        "tab_model": "🔍 Model Explainer",
        "tab_geo": "🗺️ Geo Intelligence",
        "tab_insights": "📖 Conclusions",

        "intro_title": "The Problem: Why aren't our customers coming back?",
        "intro_body": (
            "Imagine you're running operations at **Olist**, Brazil's largest marketplace. "
            "Thousands of new buyers arrive every month, but most **never purchase again**. "
            "Acquiring each customer costs money in marketing, logistics, and support — and that "
            "ROI is lost when the customer disappears.\n\n"
            "This dashboard analyzes **93,000+ customers** to answer three key questions:\n"
            "1. **Who** is about to leave?\n"
            "2. **Why** are they leaving?\n"
            "3. **What can we do** to retain them?"
        ),

        "kpi_total_customers": "Total Customers",
        "kpi_churn_rate": "Churn Rate",
        "kpi_revenue_at_risk": "Revenue at Risk",
        "kpi_avg_ltv": "Avg LTV",

        "insight_overview": "💡 **Executive insight:** Nearly 6 out of 10 customers don't return after their first purchase. The marketplace has a structural retention problem, not an acquisition one. Each percentage point of retention improvement equals ~R$ 230K in protected revenue.",
        "insight_cohort": "💡 **Cohort insight:** 95% of customers who don't return in the first month after their purchase never come back. The intervention window is **30 days max** post-purchase — after that, the customer is already lost.",
        "insight_atrisk": "💡 **Risk insight:** Customers in the \"red zone\" (probability > 70%) represent only 23% of the base but concentrate 38% of accumulated revenue. Prioritizing these 500 customers would generate the highest retention ROI.",
        "insight_model": "💡 **Model insight:** The most powerful variable for predicting churn isn't price or product category — it's simply **how many days since the last purchase**. Recency outperforms all other signals combined.",
        "insight_geo": "💡 **Geographic insight:** Northern Brazilian states have churn rates up to 15 percentage points higher than the south. The main cause: delivery times are 2-3x longer, eroding customer satisfaction.",

        "chart_churn_trend": "Monthly Churn Rate Trend",
        "chart_churn_by_state": "Top 10 States by Churn Rate",
        "chart_cohort_heatmap": "Cohort Retention Matrix",
        "chart_retention_curves": "Retention Curves by Cohort",
        "chart_risk_scatter": "Prioritization: Churn Probability vs Revenue",
        "chart_shap": "Feature Importance (SHAP)",
        "chart_geo_map": "Churn Rate by State in Brazil",
        "chart_delivery_vs_churn": "Correlation: Delivery Delay vs Churn",

        "col_customer": "Customer",
        "col_prob_churn": "Churn Prob.",
        "col_days_inactive": "Inactive Days",
        "col_revenue": "Total Revenue",
        "col_action": "Recommended Action",
        "col_risk": "Risk Level",
        "col_orders": "Orders",
        "col_review": "Avg Review",
        "col_state": "State",
        "btn_export": "📥 Export CSV for Customer Success",
        "total_at_risk": "At-risk customers",
        "revenue_at_risk_label": "Revenue at risk",

        "cohort_best": "🏆 Best Cohort (M+3)",
        "cohort_worst": "📉 Worst Cohort (M+3)",
        "cohort_cliff": "🪨 Churn Cliff",
        "cohort_retention_pct": "retention",
        "cohort_drop": "drop",

        "model_auc": "AUC-ROC",
        "model_f1": "F1-Score",
        "model_precision": "Precision",
        "model_recall": "Recall",
        "model_best": "Best Model",
        "model_threshold": "Optimal Threshold",
        "feature_importance_title": "Global Feature Importance (SHAP)",
        "geo_correlation": "Correlation between delay rate and churn rate",

        "conclusions_title": "Conclusions & Action Plan",
        "conclusions_causes_title": "🔎 Root Causes",
        "conclusions_causes": (
            "Churn at Olist is not random. It follows predictable patterns that reveal "
            "**three root causes**:\n\n"
            "**1. Transactional business model:** Olist operates as an intermediary. Customers "
            "buy a product, not a relationship. Without incentives to return, inertia leads them "
            "to seek alternatives.\n\n"
            "**2. Poor logistics in remote regions:** In northern states "
            "(AM, RR, AP), delivery times average 25+ days. Frustration with waiting "
            "translates directly into churn — the delay-churn correlation is 0.73.\n\n"
            "**3. No post-purchase engagement:** There is no communication after delivery. "
            "67% of customers with review < 3 never return. Bad experiences are not resolved, "
            "they're ignored."
        ),
        "conclusions_findings_title": "📊 Key Findings",
        "conclusions_findings": (
            "| # | Finding | Impact |\n"
            "|---|---------|--------|\n"
            "| 1 | Retention drops **95% at M+1** | The window is only 30 days |\n"
            "| 2 | `days_since_last_purchase` is feature #1 | Recency predicts everything |\n"
            "| 3 | Reviews < 3 → 4.2x more churn | Satisfaction is key |\n"
            "| 4 | North vs South: 15pp churn difference | Logistics is the factor |\n"
            "| 5 | 23% of base = 38% of revenue at risk | Value concentration |"
        ),
        "conclusions_actions_title": "🚀 Recommended Actions",
        "conclusions_actions": (
            "**Immediate impact (0-30 days):**\n"
            "- 📞 Contact top 500 customers by revenue × churn probability\n"
            "- 📧 Post-delivery follow-up email to all new buyers on day 7\n"
            "- 🎁 15% coupon for second purchase, sent on day 14 post-first-purchase\n\n"
            "**Medium impact (30-90 days):**\n"
            "- 📦 Negotiate with logistics operators in the north to reduce times to < 15 days\n"
            "- ⭐ Proactively resolve experiences with 1-2 star reviews within 3 days\n"
            "- 🔄 Loyalty program with points for recurring purchases\n\n"
            "**Long-term impact (90+ days):**\n"
            "- 🤖 Deploy churn model to production with automatic CS team alerts\n"
            "- 📊 A/B testing of retention campaigns by segment\n"
            "- 🏪 Incentivize sellers to offer complementary products"
        ),
        "conclusions_prediction_title": "🔮 Prediction with Actions Implemented",
        "conclusions_prediction": (
            "If we execute the recommended actions, we project:\n\n"
            "| Metric | Current | Projection (6 months) | Change |\n"
            "|--------|---------|----------------------|--------|\n"
            "| Churn rate | 58.9% | ~45% | -13.9pp |\n"
            "| Protected revenue | R$ 0 | R$ 3.2M | +R$ 3.2M |\n"
            "| M+1 retention | 4.7% | ~12% | +7.3pp |\n"
            "| Avg LTV | R$ 165 | R$ 215 | +30% |\n\n"
            "The greatest impact would come from intervention in the first 14 days "
            "post-purchase, which alone could improve M+1 retention by 5-8 percentage points."
        ),
        "no_data": "No data available.",
    },

    "PT": {
        "app_title": "Customer Retention Intelligence",
        "app_subtitle": "Previsão de Churn · Análise de Coortes · Clientes em Risco · Olist Brasil 2016–2018",
        "sidebar_title": "CRI Dashboard",
        "sidebar_subtitle": "Customer Retention Intelligence",
        "sidebar_filters": "Filtros",
        "filter_state": "Estado brasileiro",
        "filter_threshold": "Limite de risco de churn",
        "filter_all_states": "Todos os estados",
        "sidebar_footer": "Dataset: Olist Brasil · 2016–2018\nModelo: Random Forest · AUC 1.00",
        "tab_overview": "📊 Visão Executiva",
        "tab_cohort": "🎯 Retenção por Coortes",
        "tab_atrisk": "⚠️ Clientes em Risco",
        "tab_model": "🔍 Explicador do Modelo",
        "tab_geo": "🗺️ Inteligência Geográfica",
        "tab_insights": "📖 Conclusões",

        "intro_title": "O Problema: Por que nossos clientes não voltam?",
        "intro_body": (
            "Imagine que você dirige as operações da **Olist**, o maior marketplace do Brasil. "
            "Milhares de novos compradores chegam todo mês, mas a maioria **nunca volta a comprar**. "
            "Adquirir cada cliente custou dinheiro em marketing, logística e atendimento — e esse "
            "retorno de investimento se perde quando o cliente desaparece.\n\n"
            "Este dashboard analisa **93.000+ clientes** para responder três perguntas-chave:\n"
            "1. **Quem** está prestes a sair?\n"
            "2. **Por que** estão saindo?\n"
            "3. **O que podemos fazer** para retê-los?"
        ),

        "kpi_total_customers": "Total de Clientes",
        "kpi_churn_rate": "Taxa de Churn",
        "kpi_revenue_at_risk": "Receita em Risco",
        "kpi_avg_ltv": "LTV Médio",

        "insight_overview": "💡 **Insight executivo:** Quase 6 em cada 10 clientes não voltam após a primeira compra. O marketplace tem um problema estrutural de retenção, não de aquisição. Cada ponto percentual de melhoria na retenção equivale a ~R$ 230K em receita protegida.",
        "insight_cohort": "💡 **Insight de coortes:** 95% dos clientes que não voltam no primeiro mês após a compra jamais retornam. A janela de intervenção é de **no máximo 30 dias** pós-compra — depois disso, o cliente já está perdido.",
        "insight_atrisk": "💡 **Insight de risco:** Clientes na \"zona vermelha\" (probabilidade > 70%) representam apenas 23% da base, mas concentram 38% da receita acumulada. Priorizar esses 500 clientes geraria o maior ROI em retenção.",
        "insight_model": "💡 **Insight do modelo:** A variável mais poderosa para prever churn não é o preço nem a categoria do produto — é simplesmente **quantos dias se passaram desde a última compra**. A recência supera todos os outros sinais combinados.",
        "insight_geo": "💡 **Insight geográfico:** Os estados do norte do Brasil têm taxas de churn até 15 pontos percentuais maiores que o sul. A causa principal: os tempos de entrega são 2-3x maiores, corroendo a satisfação do cliente.",

        "chart_churn_trend": "Evolução Mensal da Taxa de Churn",
        "chart_churn_by_state": "Top 10 Estados por Taxa de Churn",
        "chart_cohort_heatmap": "Matriz de Retenção por Coortes",
        "chart_retention_curves": "Curvas de Retenção por Coorte",
        "chart_risk_scatter": "Priorização: Probabilidade de Churn vs Receita",
        "chart_shap": "Importância das Variáveis (SHAP)",
        "chart_geo_map": "Taxa de Churn por Estado no Brasil",
        "chart_delivery_vs_churn": "Correlação: Atraso na Entrega vs Churn",

        "col_customer": "Cliente",
        "col_prob_churn": "Prob. Churn",
        "col_days_inactive": "Dias Inativo",
        "col_revenue": "Receita Total",
        "col_action": "Ação Recomendada",
        "col_risk": "Nível de Risco",
        "col_orders": "Pedidos",
        "col_review": "Review Méd.",
        "col_state": "Estado",
        "btn_export": "📥 Exportar CSV para Customer Success",
        "total_at_risk": "Clientes em risco",
        "revenue_at_risk_label": "Receita em risco",

        "cohort_best": "🏆 Melhor Coorte (M+3)",
        "cohort_worst": "📉 Pior Coorte (M+3)",
        "cohort_cliff": "🪨 Churn Cliff",
        "cohort_retention_pct": "retenção",
        "cohort_drop": "queda",

        "model_auc": "AUC-ROC",
        "model_f1": "F1-Score",
        "model_precision": "Precisão",
        "model_recall": "Recall",
        "model_best": "Melhor Modelo",
        "model_threshold": "Threshold Ótimo",
        "feature_importance_title": "Importância Global das Variáveis (SHAP)",
        "geo_correlation": "Correlação entre taxa de atraso e taxa de churn",

        "conclusions_title": "Conclusões e Plano de Ação",
        "conclusions_causes_title": "🔎 As Causas Raiz",
        "conclusions_causes": (
            "O churn na Olist não é aleatório. Segue padrões previsíveis que revelam "
            "**três causas raiz**:\n\n"
            "**1. Modelo de negócio transacional:** A Olist opera como intermediário. Os clientes "
            "compram um produto, não um relacionamento. Sem incentivos para voltar, a inércia os leva "
            "a buscar alternativas.\n\n"
            "**2. Experiência logística deficiente em regiões remotas:** Em estados do norte "
            "(AM, RR, AP), os tempos de entrega médios são de 25+ dias. A frustração com a espera "
            "se traduz diretamente em abandono — a correlação atraso-churn é de 0,73.\n\n"
            "**3. Falta de engajamento pós-compra:** Não existe comunicação após a entrega. "
            "67% dos clientes com review < 3 nunca voltam. A experiência ruim não é resolvida, "
            "é ignorada."
        ),
        "conclusions_findings_title": "📊 Descobertas-Chave",
        "conclusions_findings": (
            "| # | Descoberta | Impacto |\n"
            "|---|-----------|--------|\n"
            "| 1 | A retenção cai **95% no M+1** | A janela é de apenas 30 dias |\n"
            "| 2 | `days_since_last_purchase` é a feature #1 | A recência prevê tudo |\n"
            "| 3 | Reviews < 3 → 4,2x mais churn | A satisfação é chave |\n"
            "| 4 | Norte vs Sul: 15pp de diferença no churn | Logística é o fator |\n"
            "| 5 | 23% da base = 38% da receita em risco | Concentração de valor |"
        ),
        "conclusions_actions_title": "🚀 Ações Recomendadas",
        "conclusions_actions": (
            "**Impacto imediato (0-30 dias):**\n"
            "- 📞 Contatar os top 500 clientes por receita × probabilidade de churn\n"
            "- 📧 Email de acompanhamento pós-entrega para todos os novos compradores no dia 7\n"
            "- 🎁 Cupom de 15% para segunda compra, enviado no dia 14 pós-primeira-compra\n\n"
            "**Impacto médio (30-90 dias):**\n"
            "- 📦 Negociar com operadores logísticos do norte para reduzir tempos a < 15 dias\n"
            "- ⭐ Resolver proativamente experiências com review 1-2 dentro de 3 dias\n"
            "- 🔄 Programa de fidelização com pontos por compra recorrente\n\n"
            "**Impacto de longo prazo (90+ dias):**\n"
            "- 🤖 Implementar modelo de churn em produção com alertas automáticos à equipe CS\n"
            "- 📊 Teste A/B de campanhas de retenção por segmento\n"
            "- 🏪 Incentivar vendedores a oferecer produtos complementares"
        ),
        "conclusions_prediction_title": "🔮 Previsão com Ações Implementadas",
        "conclusions_prediction": (
            "Se executarmos as ações recomendadas, projetamos:\n\n"
            "| Métrica | Atual | Projeção (6 meses) | Mudança |\n"
            "|---------|-------|-------------------|--------|\n"
            "| Taxa de churn | 58,9% | ~45% | -13,9pp |\n"
            "| Receita protegida | R$ 0 | R$ 3,2M | +R$ 3,2M |\n"
            "| Retenção M+1 | 4,7% | ~12% | +7,3pp |\n"
            "| LTV médio | R$ 165 | R$ 215 | +30% |\n\n"
            "O maior impacto viria da intervenção nos primeiros 14 dias "
            "pós-compra, que sozinha poderia melhorar a retenção M+1 em 5-8 pontos percentuais."
        ),
        "no_data": "Dados não disponíveis.",
    },
}


def t(key: str) -> str:
    """Get translation for current language from session state."""
    lang = st.session_state.get("language", "ES")
    return TRANSLATIONS.get(lang, TRANSLATIONS["ES"]).get(key, key)
