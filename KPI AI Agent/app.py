import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import modules from src
from src.data_pipeline import load_data
from src.eda import plot_kpi_distribution
from src.ahp_module import create_criteria_comparison

st.title("Remote Fix KPI Analysis Dashboard")

# Load data from the CSV files in the data folder
q1_file = "data/cases_Q1_current_year.csv"
q4_file = "data/cases_Q4_2024.csv"
q1_data = load_data(q1_file)
q4_data = load_data(q4_file)

# Display data summaries
st.header("Data Overview")
st.subheader("Q1 Data Summary")
st.write(q1_data.describe())
st.subheader("Q4 Data Summary")
st.write(q4_data.describe())

# KPI Distribution Comparison Plot
st.header("KPI Distribution Comparison")
fig = plot_kpi_distribution(q1_data, q4_data, kpi='resolution_time')
st.pyplot(fig)

# AHP Decision Analysis Section
st.header("AHP Decision Analysis")
st.write("Adjust the criteria importance using the sliders below:")

# Interactive sliders for AHP weights
case_complexity_vs_staff = st.slider("Case Complexity vs Staffing Levels", 1, 9, 3)
case_complexity_vs_process = st.slider("Case Complexity vs Process Changes", 1, 9, 5)
case_complexity_vs_tech = st.slider("Case Complexity vs Technology Adjustments", 1, 9, 7)

# Update the AHP comparisons using the slider input
custom_weights = {
    ('Case Complexity', 'Staffing Levels'): case_complexity_vs_staff,
    ('Case Complexity', 'Process Changes'): case_complexity_vs_process,
    ('Case Complexity', 'Technology Adjustments'): case_complexity_vs_tech,
}
criteria = create_criteria_comparison(custom_weights=custom_weights)
report_str = criteria.report()

st.text(report_str)
