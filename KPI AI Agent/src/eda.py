import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas_profiling import ProfileReport

def generate_eda_report(df, title="EDA Report", explorative=True, minimal=False):
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if minimal:
        explorative = False  # Minimal mode overrides explorative
    
    profile = ProfileReport(
        df,
        title=title,
        explorative=explorative,
        minimal=minimal,
        progress_bar=False  # Disable for cleaner output
    )
    profile.to_file(f"{title}.html")
    return profile
    
def plot_kpi_distribution(q1_df, q4_df, kpi='resolution_time'):
if kpi not in q1_df.columns or kpi not in q4_df.columns:
        raise ValueError(f"Column '{kpi}' not found in one of the DataFrames")
    if not pd.api.types.is_numeric_dtype(q1_df[kpi]):
        raise TypeError(f"Column '{kpi}' must be numeric for KDE plot")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot KDEs
    sns.kdeplot(q1_df[kpi], shade=True, ax=ax, label='Q1 This Year')
    sns.kdeplot(q4_df[kpi], shade=True, ax=ax, label='Q4 2024')
    
    # Formatting
    ax.set_title(f"Distribution of {kpi.title()} Comparison", fontsize=14)
    ax.set_xlabel(f"{kpi.title()} (Unit)", fontsize=12)  # Customize unit as needed
    ax.set_ylabel("Density", fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig

if __name__ == '__main__':
    try:
        # Use the improved load_data function
        q1 = load_data(
            file_path='../data/cases_Q1_current_year.csv',
            date_col='date',
            fillna_columns=['resolution_time', 'cost']
        )
        q4 = load_data(
            file_path='../data/cases_Q4_2024.csv',
            date_col='date',
            fillna_columns=['resolution_time', 'cost']
        )
        
        # Generate EDA report for Q1
        profile = generate_eda_report(q1, title="Q1 EDA Report", minimal=True)
        profile.to_file("q1_eda_report.html")
        
        # Plot KPI distribution
        fig = plot_kpi_distribution(q1, q4, kpi='resolution_time')
        plt.show()
        
    except Exception as e:
        print(f"Error: {str(e)}")
