import requests
import os
import json
import folium
from folium.plugins import HeatMap
from dotenv import load_dotenv

load_dotenv()

APP_TOKEN = os.getenv("NYC_APP_TOKEN")
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

def fetch_311_data():
    if not APP_TOKEN:
        print("No app token found")

    params = {
        "$$app_token": APP_TOKEN,
        "$order": "created_date DESC",
        "complaint_type": "Noise"
    }
    try:

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() 
        data = response.json()
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        print(f"Response Content: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

def main():
    requests = fetch_311_data()

    coordinates = []
    for request in requests:
        try:
            lat = float(request.get("latitude", 0))
            lon = float(request.get("longitude", 0))
            if lat != 0 and lon != 0:  # Skip invalid coordinates
                coordinates.append([lat, lon])
        except (ValueError, TypeError):
            continue  # Skip invalid data

    map = folium.Map([40.0, -73.0], zoom_start=6)
    HeatMap(coordinates).add_to(map)
    map.save('index.html')

if __name__ == "__main__":
    main()
