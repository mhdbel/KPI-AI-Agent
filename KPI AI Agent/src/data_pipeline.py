import pandas as pd

def load_data(file_path, date_col='date', fillna_columns=None):
    """
    Loads a CSV file into a pandas DataFrame, parses the specified date column,
    and optionally fills missing values for specific columns.

    Args:
        file_path (str): Path to the CSV file.
        date_col (str, optional): Column name to parse as datetime. Defaults to 'date'.
        fillna_columns (list, optional): Columns to forward-fill missing values. Defaults to None (no filling).

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    try:
        # Load data with error handling for invalid paths/columns
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
            df[col] = df[col].fillna(method='ffill')
            # Handle leading NaNs (replace with backward fill if possible)
            df[col] = df[col].bfill()  # or fill with a default value

    return df

if __name__ == "__main__":
    try:
        # Test the data loader with explicit parameters
        df = load_data(
            file_path='../data/cases_Q1_current_year.csv',
            date_col='date',  # Match the actual column name
            fillna_columns=['resolution_time', 'cost']  # Specify columns to forward-fill
        )
        print(df.head())
        print("Missing values:\n", df.isnull().sum())
    except Exception as e:
        print(f"Error: {str(e)}")
