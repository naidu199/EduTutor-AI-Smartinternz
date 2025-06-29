import os
import requests

api_key = os.getenv("IBM_API_KEY")
project_id = os.getenv("IBM_PROJECT_ID")

print(f"API Key exists: {bool(api_key)}")
print(f"Project ID exists: {bool(project_id)}")

if api_key and project_id:
    try:
        # Test token generation
        token_url = "https://iam.cloud.ibm.com/identity/token"
        data = {
            "grant_type": "urn:iam:grant-type:apikey",
            "apikey": api_key
        }
        response = requests.post(token_url, data=data, timeout=10)
        print(f"Token response: {response.status_code}")
        if response.status_code == 200:
            print("Authentication successful")
        else:
            print(f"Auth failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")