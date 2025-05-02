# KPI-AI-Agent

This repository contains code for an AI agent that:
- Retrieves and preprocesses remote fix case data (either from CSV files or directly from a Power BI dataset)
- Generates exploratory data analysis (EDA) reports and predictive analytics
- Implements Analytic Hierarchy Process (AHP) for prioritizing corrective actions
- Provides an interactive dashboard via Streamlit for real-time insights

## Data Sources

In addition to CSV files located in the `data/` directory, you can also extract data directly from a Power BI source using the Power BI REST API. To do so, you must:
1. Register your application in the Azure portal.
2. Obtain an OAuth access token.
3. Prepare your dataset ID and table names.

## Repository Structure
my-ai-agent/
├── README.md
├── requirements.txt
├── data/
│   ├── cases_Q1_current_year.csv
│   └── cases_Q4_2024.csv
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py
│   ├── eda.py
│   ├── predictive.py
│   ├── ahp_module.py
│   └── powerbi.py
└── app.py

