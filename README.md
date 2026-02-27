# 🔄 Churn Prediction + Cohort Retention Dashboard

Sistema de predicción de churn y análisis de retención por cohortes para e-commerce, 
construido con datos reales del dataset Olist (Brasil, 2016–2018).

## 📋 Descripción

Este proyecto implementa un pipeline completo de Data Science que:

1. **Predice con 30 días de anticipación** qué clientes están en riesgo de cancelar
2. **Visualiza la retención histórica** por cohortes en un dashboard interactivo
3. **Explica las predicciones** con SHAP values para cada cliente

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| ETL & Features | pandas, numpy, pyarrow |
| Modelos ML | scikit-learn, XGBoost, LightGBM |
| Explicabilidad | SHAP |
| Dashboard | Streamlit + Plotly |
| Dataset | Olist Brazilian E-commerce (Kaggle) |

## 📁 Estructura del Proyecto

```
customer-retention-intelligence/
├── AGENTS.md                    # Documentación de los agentes del pipeline
├── SKILLS.md                    # Habilidades técnicas utilizadas
├── requirements.txt             # Dependencias con versiones fijas
├── README.md                    # Este archivo
├── data/
│   ├── raw/                     # 9 CSVs originales de Olist
│   ├── processed/               # Datos transformados (parquet)
│   └── outputs/                 # Resultados y predicciones
│       └── logs/                # Logs de ejecución
├── pipeline/
│   ├── 01_etl.py                # Agente 1: ETL y tabla maestra
│   ├── 02_feature_engineering.py # Agente 2: Feature engineering
│   ├── 03_churn_model.py        # Agente 3: Modelo de churn
│   ├── 04_cohort_analysis.py    # Agente 4: Análisis de cohortes
│   └── 05_insights_generator.py # Agente 5: Generador de insights
├── dashboard/
│   ├── app.py                   # Dashboard principal (Streamlit)
│   ├── components/              # Componentes visuales
│   │   ├── kpi_cards.py
│   │   ├── cohort_heatmap.py
│   │   ├── churn_risk_table.py
│   │   ├── geo_map.py
│   │   └── model_explainer.py
│   └── utils.py                 # Utilidades de carga de datos
├── models/                      # Modelos entrenados (.pkl)
└── tests/                       # Tests del proyecto
```

## 🚀 Cómo Ejecutar

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Descargar el dataset
Descarga el [dataset de Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) 
de Kaggle y coloca los 9 archivos CSV en `data/raw/`.

### 3. Ejecutar el pipeline (en orden)
```bash
python pipeline/01_etl.py
python pipeline/02_feature_engineering.py
python pipeline/03_churn_model.py
python pipeline/04_cohort_analysis.py
python pipeline/05_insights_generator.py
```

### 4. Lanzar el dashboard
```bash
streamlit run dashboard/app.py
```

## 📊 Dashboard

El dashboard tiene 5 pestañas:

| Pestaña | Contenido |
|---------|-----------|
| **Executive Overview** | KPIs, evolución del churn, top estados |
| **Cohort Retention** | Heatmap de retención, curvas por cohorte |
| **At-Risk Customers** | Tabla de clientes en riesgo, scatter de priorización |
| **Model Explainer** | SHAP values, importancia de features |
| **Geo Intelligence** | Mapa coroplético, correlación delivery vs churn |

## 🤖 Modelos Entrenados

Se comparan 4 modelos con split temporal (sin data leakage):
- Logistic Regression (baseline)
- Random Forest
- **XGBoost** (modelo principal)
- LightGBM

Métricas: ROC-AUC + F1-Score. Se optimiza el threshold para maximizar recall en la clase churned.

## 📝 Notas

- Cada script puede ejecutarse de forma independiente
- Si un archivo de input no existe, el script indica qué ejecutar primero
- Todo el código está comentado en español
- El dashboard usa dark theme y está completamente en español
