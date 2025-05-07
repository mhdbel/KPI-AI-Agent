import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_pipeline import load_data, load_data_powerbi
from src.eda import plot_kpi_distribution
from src.ahp_module import create_criteria_comparison, AHPConfigError
from src.powerbi import get_access_token  # Ensure this function exists in your module

st.set_page_config(
    page_title="Remote Fix KPI Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CACHE FOR CSV LOADING (Performance Optimization)
@st.cache_data
def load_cached_data(file_path):
    return load_data(file_path)

# SIDEBAR SETUP
st.sidebar.header("Data Source Configuration")
data_source = st.sidebar.radio(
    "Select Data Source",
    ["CSV Files", "Power BI"],
    index=0,
    help="Choose between local CSV files or Power BI datasets."
)

# Initialize session state for Power BI data
if "q1_data" not in st.session_state:
    st.session_state.q1_data = None
if "q4_data" not in st.session_state:
    st.session_state.q4_data = None

# DATA LOADING LOGIC
def load_csv_data():
    """Load CSV files with caching for performance."""
    try:
        q1_data = load_cached_data("data/cases_Q1_current_year.csv")
        q4_data = load_cached_data("data/cases_Q4_2024.csv")
        return q1_data, q4_data
    except Exception as e:
        st.error(f"Error loading CSV files: {str(e)}")
        return None, None

def load_powerbi_data():
    """Secure Power BI data loading with configuration."""
    with st.sidebar.expander("Power BI Configuration"):
        dataset_id = st.text_input("Dataset ID", value="", placeholder="Enter Dataset ID")
        table_q1 = st.text_input("Q1 Table Name", value="cases_Q1_current_year")
        table_q4 = st.text_input("Q4 Table Name", value="cases_Q4_2024")
        access_token = st.text_input(
            "Access Token",
            type="password",
            value="",
            placeholder="Paste Access Token Here"
        )
        
        if st.button("Load Power BI Data"):
            if not all([dataset_id, table_q1, table_q4, access_token]):
                st.error("All Power BI fields are required!")
                return None, None
            
            try:
                # Load data securely
                q1_config = {
                    "dataset_id": dataset_id,
                    "table_name": table_q1,
                    "access_token": access_token
                }
                q4_config = {
                    "dataset_id": dataset_id,
                    "table_name": table_q4,
                    "access_token": access_token
                }
                
                q1_data = load_data_powerbi(q1_config)
                q4_data = load_data_powerbi(q4_config)
                
                if q1_data.empty or q4_data.empty:
                    st.error("Power BI returned empty datasets. Check table names and permissions.")
                    return None, None
                
                st.session_state.q1_data = q1_data
                st.session_state.q4_data = q4_data
                st.success("Power BI data loaded successfully!", icon="✅")
                return q1_data, q4_data
                
            except Exception as e:
                st.error(f"Failed to load Power BI data: {str(e)}")
                return None, None
    return st.session_state.q1_data, st.session_state.q4_data

# Load data based on source selection
if data_source == "CSV Files":
    q1_data, q4_data = load_csv_data()
else:
    q1_data, q4_data = load_powerbi_data()

# Check if data is loaded
if q1_data is not None and q4_data is not None:
    # DATA OVERVIEW
    st.header("📊 Data Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Q1 Data Summary")
        st.dataframe(q1_data.describe(), use_container_width=True)
        
    with col2:
        st.subheader("Q4 Data Summary")
        st.dataframe(q4_data.describe(), use_container_width=True)
    
    # KPI SELECTION & PLOTTING
    st.header("📈 KPI Distribution Comparison")
    numeric_cols = list(q1_data.select_dtypes(include="number").columns)
    default_kpi = "resolution_time" if "resolution_time" in numeric_cols else numeric_cols[0]
    selected_kpi = st.selectbox(
        "Select KPI",
        numeric_cols,
        index=numeric_cols.index(default_kpi),
        key="kpi_selector"
    )
    
    if selected_kpi not in q4_data.columns:
        st.error(f"⚠️ KPI '{selected_kpi}' not found in Q4 data. Select another KPI.")
    else:
        try:
            fig = plot_kpi_distribution(q1_data, q4_data, kpi=selected_kpi)
            st.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error plotting KPI: {str(e)}")

    # AHP DECISION ANALYSIS
    st.header("🎯 AHP Decision Analysis")
    st.write("Adjust criteria importance using the sliders below:")
    
    try:
        # Get default criteria comparisons dynamically
        default_criteria = create_criteria_comparison()
        criteria_pairs = list(default_criteria.comparisons.keys())
        
        # Create sliders for each criteria pair
        slider_values = {}
        for pair in criteria_pairs:
            label = f"{pair[0]} vs {pair[1]}"
            default_val = default_criteria.comparisons[pair]
            slider = st.slider(
                label,
                1, 9,
                default_val,
                key=f"ahp_{pair[0]}_{pair[1]}",
                help="1 (Equal) to 9 (Extremely More Important)"
            )
            slider_values[pair] = slider
        
        # Update custom weights
        custom_weights = {pair: slider_values[pair] for pair in criteria_pairs}
        
        # Validate AHP consistency
        try:
            criteria = create_criteria_comparison(custom_weights=custom_weights)
            cr = criteria.consistency_ratio
            
            if cr > 0.1:
                st.error(f"⚠️ Consistency Ratio (CR={cr:.2f}) exceeds 0.1. Adjust comparisons.")
            else:
                st.success(f"✅ Consistency Ratio (CR={cr:.2f}) is acceptable (CR < 0.1)")
                
                # Display results with visualization
                st.subheader("Final Criteria Weights")
                weights = criteria.weights
                fig_ahp, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=list(weights.keys()), y=list(weights.values()), ax=ax)
                ax.set_title("Prioritized Criteria Weights")
                ax.set_ylabel("Weight")
                st.pyplot(fig_ahp)
                
                if st.checkbox("Show Full AHP Report"):
                    st.text(criteria.report())
                    
        except AHPConfigError as e:
            st.error(f"AHP Configuration Error: {str(e)}")
            
    except Exception as e:
        st.error(f"Failed to initialize AHP: {str(e)}")

# FOOTER & DEPLOYMENT NOTES
st.sidebar.markdown("### Deployment Notes")
st.sidebar.info(
    "To deploy, ensure:\n"
    "1. Add `secrets.toml` for Power BI credentials.\n"
    "2. Install dependencies via `requirements.txt`.\n"
    "3. Use Streamlit Sharing for cloud deployment."
)

# ERROR HANDLING FOR UNLOADED DATA
if q1_data is None or q4_data is None:
    st.warning("⚠️ No data loaded. Configure data source settings and reload.")
