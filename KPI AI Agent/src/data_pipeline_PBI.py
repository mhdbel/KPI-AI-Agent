import pandas as pd
from src.powerbi import load_data_from_powerbi

def load_data(file_path, date_col='date', fillna_columns=None):
    try:
        df = pd.read_csv(file_path, parse_dates=[date_col])
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except KeyError:
        raise ValueError(f"Column '{date_col}' not found in the CSV")

    # Validate date parsing
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        raise TypeError(f"Column '{date_col}' could not be parsed as datetime")

    # Handle missing values selectively
    if fillna_columns:
        for col in fillna_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in the DataFrame")
            # Forward-fill and handle leading NaNs with backward-fill
            df[col] = df[col].fillna(method='ffill')
            df[col] = df[col].fillna(method='bfill')  # Handle leading NaNs
            # Alternatively, fill with default values like mean/median

    return df

def load_data_powerbi(source_config, date_col='date', fillna_columns=None):
    required_keys = ['dataset_id', 'table_name', 'access_token']
    for key in required_keys:
        if key not in source_config:
            raise KeyError(f"Missing required key: {key}")

    try:
        df = load_data_from_powerbi(
            dataset_id=source_config['dataset_id'],
            table_name=source_config['table_name'],
            access_token=source_config['access_token']
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load Power BI data: {str(e)}")

    # Parse date column
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if df[date_col].isnull().all():
            raise ValueError(f"Column '{date_col}' could not be parsed as datetime")
    else:
        print(f"Warning: '{date_col}' not found. Skipping date parsing.")

    # Handle missing values selectively
    if fillna_columns:
        for col in fillna_columns:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in the DataFrame")
            df[col] = df[col].fillna(method='ffill').fillna(method='bfill')

    return df

if __name__ == "__main__":
    try:
        # Test CSV loader with parameters
        df_csv = load_data(
            file_path='../data/cases_Q1_current_year.csv',
            date_col='date',
            fillna_columns=['resolution_time', 'cost']
        )
        print("CSV Data:\n", df_csv.head())
        print("Missing values:\n", df_csv.isnull().sum())

        # Test Power BI loader (mock config for demonstration)
        powerbi_config = {
            'dataset_id': 'your_dataset_id',
            'table_name': 'cases_table',
            'access_token': 'your_access_token'
        }
        df_powerbi = load_data_powerbi(
            source_config=powerbi_config,
            date_col='date',
            fillna_columns=['resolution_time', 'cost']
        )
        print("\nPower BI Data:\n", df_powerbi.head())
        print("Missing values:\n", df_powerbi.isnull().sum())
        
    except Exception as e:
        print(f"Error: {str(e)}")
