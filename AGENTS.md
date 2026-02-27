# Agentes del Pipeline — Churn Prediction

## Agente 1 — ETL (`pipeline/01_etl.py`)
Une los 9 CSVs de Olist en una tabla maestra por `customer_unique_id`.
Solo procesa órdenes con status `delivered`.

## Agente 2 — Feature Engineering (`pipeline/02_feature_engineering.py`)
Construye features de recencia, frecuencia, monetario, satisfacción y logística.
Define churn label: sin compra en últimos 180 días → churned.

## Agente 3 — Modelo ML (`pipeline/03_churn_model.py`)
Entrena LR, RF, XGBoost, LightGBM con split temporal.
Selecciona el mejor modelo por ROC-AUC. Genera SHAP values.

## Agente 4 — Cohort Analysis (`pipeline/04_cohort_analysis.py`)
Construye matriz de retención mensual por cohortes (clientes y revenue).

## Agente 5 — Insights Generator (`pipeline/05_insights_generator.py`)
Agrega insights de negocio para consumo del dashboard.

## Dashboard (`dashboard/app.py`)
Streamlit + Plotly. 5 pestañas: Overview, Cohorts, At-Risk, Explainer, Geo.