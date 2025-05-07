import requests
import pandas as pd
from requests.exceptions import HTTPError

def load_data_from_powerbi(dataset_id, table_name, access_token, top=1000):
    """
    Fetch data from a Power BI dataset using the Power BI Data Access API.
    
    Args:
        dataset_id (str): Power BI dataset ID.
        table_name (str): Table name in the dataset.
        access_token (str): OAuth Bearer token for authentication.
        top (int): Maximum number of rows to retrieve (default=1000).
        
    Returns:
        pd.DataFrame: Fetched data.
    """
    # Construct the API URL for Data Access API
    api_url = (
        f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/"
        f"tables/{table_name}/rows?$top={top}"
    )
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        # Extract data rows (structure may vary; adjust based on actual response)
        rows = data.get("value", [])
        df = pd.DataFrame(rows)
        return df

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        raise
    except Exception as err:
        print(f"Other error occurred: {err}")
        raise

if __name__ == "__main__":
    import os

    # Use environment variables for credentials
    dataset_id = os.getenv("POWERBI_DATASET_ID", "your-dataset-id")
    table_name = os.getenv("POWERBI_TABLE_NAME", "your-table-name")
    access_token = os.getenv("POWERBI_ACCESS_TOKEN", "your-oauth-token")
    
    try:
        df_powerbi = load_data_from_powerbi(
            dataset_id=dataset_id,
            table_name=table_name,
            access_token=access_token,
            top=1000  # Adjust as needed
        )
        print(df_powerbi.head())
    except Exception as e:
        print(f"Error: {str(e)}")
