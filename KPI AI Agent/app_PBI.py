import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_pipeline import load_data, load_data_powerbi
from src.eda import plot_kpi_distribution
from src.ahp_module import create_criteria_comparison

st.title("Remote Fix KPI Analysis Dashboard")

# Sidebar: Data Source Selection
data_source = st.sidebar.selectbox("Select Data Source", ["CSV Files", "Power BI"])

if data_source == "CSV Files":
    q1_file = "data/cases_Q1_current_year.csv"
    q4_file = "data/cases_Q4_2024.csv"
    q1_data = load_data(q1_file)
    q4_data = load_data(q4_file)
else:
    st.sidebar.markdown("### Configure Power BI Authentication")
    dataset_id = st.sidebar.text_input("Dataset ID", "your-dataset-id")
    table_q1 = st.sidebar.text_input("Q1 Table Name", "cases_Q1_current_year")
    table_q4 = st.sidebar.text_input("Q4 Table Name", "cases_Q4_2024")
    access_token = st.sidebar.text_input("Access Token", type="password")
    
    if dataset_id and table_q1 and table_q4 and access_token:
        q1_config = {"dataset_id": dataset_id, "table_name": table_q1, "access_token": access_token}
        q4_config = {"dataset_id": dataset_id, "table_name": table_q4, "access_token": access_token}
        q1_data = load_data_powerbi(q1_config)
        q4_data = load_data_powerbi(q4_config)
    else:
        st.error("Please fill in all Power BI configuration fields to load the data.")

# Continue if data is loaded
if 'q1_data' in locals() and 'q4_data' in locals():
    st.header("Data Overview")
    st.subheader("Q1 Data Summary")
    st.write(q1_data.describe())
    st.subheader("Q4 Data Summary")
    st.write(q4_data.describe())

    st.header("KPI Distribution Comparison")
    fig = plot_kpi_distribution(q1_data, q4_data, kpi='resolution_time')
    st.pyplot(fig)

    st.header("AHP Decision Analysis")
    st.write("Adjust the criteria importance using the sliders below:")
    case_complexity_vs_staff = st.slider("Case Complexity vs Staffing Levels", 1, 9, 3)
    case_complexity_vs_process = st.slider("Case Complexity vs Process Changes", 1, 9, 5)
    case_complexity_vs_tech = st.slider("Case Complexity vs Technology Adjustments", 1, 9, 7)

    custom_weights = {
        ('Case Complexity', 'Staffing Levels'): case_complexity_vs_staff,
        ('Case Complexity', 'Process Changes'): case_complexity_vs_process,
        ('Case Complexity', 'Technology Adjustments'): case_complexity_vs_tech,
    }
    criteria = create_criteria_comparison(custom_weights=custom_weights)
    st.text(criteria.report())
