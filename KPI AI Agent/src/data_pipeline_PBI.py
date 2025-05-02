import pandas as pd
from src.powerbi import load_data_from_powerbi

def load_data(file_path):
    """
    Loads a CSV file into a pandas DataFrame, parses the 'date' column,
    and forward-fills missing values.
    """
    df = pd.read_csv(file_path, parse_dates=['date'])
    df.fillna(method='ffill', inplace=True)
    return df

def load_data_powerbi(source_config):
    """
    Loads data from a Power BI source.
    
    Parameters:
      - source_config (dict): Should include 'dataset_id', 'table_name', and 'access_token'.
    
    Returns:
      - pandas DataFrame with the queried data.
    """
    df = load_data_from_powerbi(
        dataset_id=source_config['dataset_id'],
        table_name=source_config['table_name'],
        access_token=source_config['access_token']
    )
    # Optionally, if there's a date column, convert it and fill missing values
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.fillna(method='ffill', inplace=True)
    return df

if __name__ == "__main__":
    # Test CSV loading
    df = load_data('../data/cases_Q1_current_year.csv')
    print(df.head())
