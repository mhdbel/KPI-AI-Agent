import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging with a custom format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("powerbi_api.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)


def validate_environment_variables():
    """Check that all required environment variables are present."""
    required_vars = [
        "CLIENT_ID",
        "CLIENT_SECRET",
        "TENANT_ID",
        "GROUP_ID",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")
    logger.info("All required environment variables are present.")


def make_powerbi_request(url: str, method: str, headers=None, params=None, json_data=None, token=None) -> dict:
    """
    Makes a Power BI API request with proper error handling.

    Args:
        url (str): The API endpoint URL.
        method (str): HTTP method ("GET" or "POST").
        headers (dict, optional): HTTP headers.
        params (dict, optional): Query parameters.
        json_data (dict, optional): JSON payload for POST requests.
        token (str): OAuth2 access token.

    Returns:
        dict: JSON response from the API.
    """
    headers = headers or {"Authorization": f"Bearer {token}"}
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP Error %s: %s", response.status_code, e)
        raise
    except Exception as e:
        logger.error("Request failed: %s", str(e))
        raise


def get_access_token() -> str:
    """Obtain an OAuth2 access token using the client credentials flow."""
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    tenant_id = os.getenv("TENANT_ID")
    
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://analysis.windows.net/powerbi/api/.default"
    }
    
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        if "access_token" not in token_data:
            raise KeyError("Access token not found in response.")
        logger.info("Access token obtained successfully.")
        return token_data["access_token"]
    except requests.exceptions.HTTPError as e:
        logger.error("Failed to retrieve access token: %s", e)
        raise
    except KeyError as e:
        logger.error("Invalid token response format: %s", e)
        raise


def get_reports(group_id: str, token: str) -> dict:
    """Retrieve reports from a Power BI workspace (group)."""
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports"
    return make_powerbi_request(url, "GET", token=token)


def get_tables(dataset_id: str, token: str) -> dict:
    """Retrieve tables from a Power BI dataset."""
    url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/tables"
    return make_powerbi_request(url, "GET", token=token)


def display_reports(reports: list) -> None:
    """Display reports in a user-friendly numbered list."""
    logger.info("Available Reports:")
    for idx, report in enumerate(reports, 1):
        logger.info(
            "[%d] Name: %s | Dataset ID: %s | ID: %s",
            idx,
            report.get("name", "N/A"),
            report.get("datasetId", "N/A"),
            report.get("id", "N/A")
        )


def select_report(reports: list) -> dict:
    """Prompt the user to select a report by its index."""
    while True:
        try:
            selection = int(input("Enter the number of the report to inspect: "))
            if 1 <= selection <= len(reports):
                return reports[selection - 1]
            else:
                logger.warning("Invalid selection. Please try again.")
        except ValueError:
            logger.warning("Invalid input. Please enter a number.")


def main():
    try:
        # Validate environment variables
        validate_environment_variables()
        
        # Retrieve environment variables
        group_id = os.getenv("GROUP_ID")
        
        # Get access token
        token = get_access_token()
        
        # Get reports from the workspace
        reports_response = get_reports(group_id, token)
        reports = reports_response.get("value", [])
        if not reports:
            logger.error("No reports found in the workspace.")
            return
        
        # Display reports and let the user select one
        display_reports(reports)
        selected_report = select_report(reports)
        dataset_id = selected_report.get("datasetId")
        
        # Get tables from the selected dataset
        tables_response = get_tables(dataset_id, token)
        tables = tables_response.get("value", [])
        
        # Display tables
        logger.info("Tables in the dataset:")
        for table in tables:
            logger.info("Table Name: %s", table.get("name", "N/A"))
        
    except EnvironmentError as e:
        logger.error("Environment configuration error: %s", e)
    except requests.exceptions.HTTPError as e:
        logger.error("API request failed: %s", e)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
    finally:
        logger.info("Script execution completed.")


if __name__ == "__main__":
    main()
