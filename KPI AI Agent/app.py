import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_pipeline import load_data
from src.eda import plot_kpi_distribution
from src.ahp_module import create_criteria_comparison, AHPConfigError

st.set_page_config(page_title="Remote Fix KPI Analysis", layout="wide")

# SIDEBAR FOR FILE UPLOAD AND CONTROLS
st.sidebar.header("Data & Configuration")
data_q1 = st.sidebar.file_uploader("Upload Q1 Data (CSV)", type=["csv"])
data_q4 = st.sidebar.file_uploader("Upload Q4 Data (CSV)", type=["csv"])

# Load default data if no files uploaded
if not data_q1 or not data_q4:
    try:
        q1_data = load_data("data/cases_Q1_current_year.csv")
        q4_data = load_data("data/cases_Q4_2024.csv")
    except Exception as e:
        st.error(f"Error loading default data: {str(e)}")
        st.stop()
else:
    try:
        q1_data = load_data(data_q1)
        q4_data = load_data(data_q4)
    except Exception as e:
        st.error(f"Error loading uploaded data: {str(e)}")
        st.stop()

# DATA OVERVIEW
st.header("Data Overview")
tab1, tab2, tab3 = st.tabs(["Q1 Data", "Q4 Data", "Sample Data"])

with tab1:
    st.subheader("Q1 Statistics")
    st.dataframe(q1_data.describe(), use_container_width=True)

with tab2:
    st.subheader("Q4 Statistics")
    st.dataframe(q4_data.describe(), use_container_width=True)

with tab3:
    st.subheader("Sample Data (Q1)")
    st.dataframe(q1_data.head(5))
    st.subheader("Sample Data (Q4)")
    st.dataframe(q4_data.head(5))

# KPI DISTRIBUTION PLOT
st.header("KPI Distribution Comparison")
numeric_cols = list(q1_data.select_dtypes(include="number").columns)
selected_kpi = st.selectbox("Select KPI", numeric_cols, index=numeric_cols.index("resolution_time"))

try:
    fig = plot_kpi_distribution(q1_data, q4_data, kpi=selected_kpi)
    st.pyplot(fig)
except Exception as e:
    st.error(f"Plotting error: {str(e)}")

# AHP DECISION ANALYSIS
st.header("AHP Decision Analysis")
st.write("Adjust criteria importance using the sliders below:")

# Generate dynamic sliders based on criteria pairs
try:
    # Get default criteria pairs from the AHP module
    default_comparisons = create_criteria_comparison().comparisons
    criteria_pairs = list(default_comparisons.keys())
    
    slider_values = {}
    for pair in criteria_pairs:
        label = f"{pair[0]} vs {pair[1]}"
        default = default_comparisons[pair]
        slider = st.slider(
            label,
            1, 9,
            default,
            key=f"slider_{pair}",
            help="1 (Equal) to 9 (Extremely More Important)"
        )
        slider_values[pair] = slider
    
    # Update custom weights
    custom_weights = {pair: slider_values[pair] for pair in criteria_pairs}
    
    # Validate AHP consistency
    try:
        criteria = create_criteria_comparison(custom_weights=custom_weights)
        if criteria.consistency_ratio > 0.1:
            st.error(f"Consistency Ratio (CR={criteria.consistency_ratio:.2f}) exceeds 0.1. Adjust comparisons.")
            st.stop()
        
        # Display results
        st.subheader("AHP Results")
        st.markdown(f"**Consistency Ratio (CR):** {criteria.consistency_ratio:.2f} ✅ (CR < 0.1)")
        st.write("Final Criteria Weights:")
        st.json(criteria.weights)
        
        # Display detailed report
        if st.checkbox("Show Full Report"):
            st.text(criteria.report())
            
    except AHPConfigError as e:
        st.error(f"AHP Error: {str(e)}")
        
except Exception as e:
    st.error(f"Failed to initialize AHP: {str(e)}")

# FOOTER
st.sidebar.markdown("---")
st.sidebar.info("💡 Tips: Upload CSV files or use defaults. Adjust sliders to refine criteria importance.")
