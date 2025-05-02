import requests
import pandas as pd

def load_data_from_powerbi(dataset_id, table_name, access_token):
    """
    Load data from a Power BI dataset using the Power BI REST API.
    
    Parameters:
      - dataset_id (str): The ID of the Power BI dataset.
      - table_name (str): The name of the table to query within the dataset.
      - access_token (str): OAuth access token for authentication.
      
    Returns:
      - df (pandas.DataFrame): DataFrame containing the queried rows.
    """
    api_url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/tables/{table_name}/rows"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # The API returns an object with a key "value" that holds a list of rows
        df = pd.DataFrame(data.get('value', []))
        return df
    else:
        response.raise_for_status()

if __name__ == '__main__':
    # Example usage (you must replace these with your actual credentials and IDs)
    dataset_id = "your-dataset-id"
    table_name = "your-table-name"
    access_token = "your-oauth-access-token"
    
    try:
        df_powerbi = load_data_from_powerbi(dataset_id, table_name, access_token)
        print(df_powerbi.head())
    except Exception as e:
        print(f"An error occurred: {e}")
