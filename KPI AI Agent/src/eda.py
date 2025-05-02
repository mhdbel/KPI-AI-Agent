import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas_profiling import ProfileReport

def generate_eda_report(df, title="EDA Report"):
    """
    Generate a Pandas Profiling report for the DataFrame.
    """
    profile = ProfileReport(df, title=title)
    return profile

def plot_kpi_distribution(q1_df, q4_df, kpi='resolution_time'):
    """
    Plot the distribution of a KPI from two datasets.
    """
    plt.figure(figsize=(8, 6))
    sns.kdeplot(q1_df[kpi], shade=True, label='Q1 This Year')
    sns.kdeplot(q4_df[kpi], shade=True, label='Q4 2024')
    plt.title(f"{kpi} Distribution Comparison")
    plt.xlabel(kpi)
    plt.legend()
    return plt.gcf()

if __name__ == '__main__':
    # For a quick test run
    q1 = pd.read_csv('../data/cases_Q1_current_year.csv')
    q4 = pd.read_csv('../data/cases_Q4_2024.csv')
    fig = plot_kpi_distribution(q1, q4)
    plt.show()
