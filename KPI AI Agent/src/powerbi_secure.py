import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_access_token():
    """
    Obtain an OAuth2 access token using the client credentials flow.
    Raises an exception if something goes wrong.
    """
    try:
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        tenant_id = os.getenv("TENANT_ID")
        
        if not client_id or not client_secret or not tenant_id:
            raise ValueError("Missing CLIENT_ID, CLIENT_SECRET, or TENANT_ID in environment variables.")

        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }
        
        response = requests.post(token_url, headers=headers, data=payload)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise Exception("Access token not found in the response.")
        logger.info("Successfully obtained access token.")
        return token
    except Exception as e:
        logger.error("Failed to get access token: %s", e)
        raise

def get_reports(group_id, token):
    """
    Retrieve reports from the specified workspace (group).
    """
    try:
        if not group_id:
            raise ValueError("Missing group_id value.")

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        reports = response.json()
        logger.info("Successfully retrieved reports.")
        return reports
    except Exception as e:
        logger.error("Failed to retrieve reports: %s", e)
        raise

def get_tables(dataset_id, token):
    """
    Retrieve tables from a specified dataset.
    """
    try:
        if not dataset_id:
            raise ValueError("Missing dataset_id value.")

        url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/tables"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = response.json()
        logger.info("Successfully retrieved tables from dataset: %s", dataset_id)
        return tables
    except Exception as e:
        logger.error("Failed to retrieve tables: %s", e)
        raise

if __name__ == '__main__':
    try:
        # Retrieve configuration from environment variables
        GROUP_ID = os.getenv("GROUP_ID")
        
        # Obtain access token
        token = get_access_token()
        
        # Retrieve reports from the specified workspace
        reports = get_reports(GROUP_ID, token)
        logger.info("Reports in the workspace:")
        for report in reports.get("value", []):
            logger.info("Report Name: %s | Report ID: %s | Dataset ID: %s",
                        report.get('name'),
                        report.get('id'),
                        report.get('datasetId'))
        
        # Example: choose a dataset_id (replace with actual one from the report info)
        dataset_id = input("Enter the Dataset ID from the report details: ").strip()
        tables = get_tables(dataset_id, token)
        logger.info("Tables in the dataset:")
        for table in tables.get("value", []):
            logger.info("Table Name: %s", table.get("name"))
    except Exception as main_e:
        logger.error("An error occurred in the main flow: %s", main_e)
