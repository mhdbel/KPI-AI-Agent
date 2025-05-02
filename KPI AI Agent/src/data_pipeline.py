import pandas as pd

def load_data(file_path):
    """
    Loads a CSV file into a pandas DataFrame, parses the 'date' column,
    and forward-fills missing values.
    """
    df = pd.read_csv(file_path, parse_dates=['date'])
    df.fillna(method='ffill', inplace=True)
    return df

if __name__ == "__main__":
    # Test the data loader
    df = load_data('../data/cases_Q1_current_year.csv')
    print(df.head())
