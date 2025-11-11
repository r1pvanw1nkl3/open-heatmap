import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

APP_TOKEN = os.getenv("NYC_APP_TOKEN")
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

def fetch_311_data():
    if not APP_TOKEN:
        print("No app token found")
        return

    params = {
        "$$app_token": APP_TOKEN,
        "$order": "created_date DESC",
        "$limit": 100,
        "complaint_type": "Noise"
    }
    try:

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() 
        data = response.json()
        print(json.dumps(data, indent=2))

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        print(f"Response Content: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

def main():
    fetch_311_data()


if __name__ == "__main__":
    main()
