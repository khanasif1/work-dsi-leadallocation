import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

if not API_URL:
    raise ValueError("API_URL environment variable not set. Please check your .env file.")

def fetch_leads_data():
    """Fetch leads data from the API and return as JSON."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)} 