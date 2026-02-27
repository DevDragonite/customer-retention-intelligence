"""
config.py — Design Tokens & Plotly Theme
=========================================
Color palette and Plotly configuration for Customer Retention Intelligence.
"""

COLORS = {
    "primary": "#9E6240",
    "secondary": "#DEA47E",
    "accent": "#CD4631",
    "base": "#F8F2DC",
    "contrast": "#81ADC8",
    "bg_dark": "#1C1410",
    "text_dark": "#2E1F14",
    "text_light": "#F8F2DC",
    "churn_high": "#CD4631",
    "churn_medium": "#DEA47E",
    "churn_low": "#81ADC8",
    "retention_good": "#81ADC8",
    "retention_warning": "#DEA47E",
    "retention_critical": "#CD4631",
}

PLOTLY_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#F8F2DC",
    "colorscale_retention": [
        [0.0, "#CD4631"],
        [0.25, "#9E6240"],
        [0.5, "#DEA47E"],
        [1.0, "#81ADC8"],
    ],
    "colorscale_churn": [
        [0.0, "#81ADC8"],
        [0.5, "#DEA47E"],
        [1.0, "#CD4631"],
    ],
}
