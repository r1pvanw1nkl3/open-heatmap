import requests
import os
import json
import folium
from folium.plugins import HeatMap
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_TOKEN = os.getenv("NYC_APP_TOKEN")
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

def fetch_311_data():
    if not APP_TOKEN:
        print("No app token found")
        return
    
    offset = 0
    end_of_data = False
    data = []

    while not end_of_data:
        params = {
            "$$app_token": APP_TOKEN,
            "$order": "created_date DESC",
            "$limit": 1000,
            "$offset": offset,
            "$where": "created_date > '2025-01-01T00:00:00' and upper(complaint_type) like '%NOISE%'"
        }
        try:

            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            new_data = response.json()

            if len(new_data) == 0:
                end_of_data = True
            else:
                print(f"{len(new_data)} new records fetched")
                data += new_data
                print(f"{len(data)} total records fetched")
                offset += 1000

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error: {http_err}")
            print(f"Response Content: {response.text}")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")

    return data

def get_popup_text(request):
    popup_text = ""
    created = request.get("created_date", None)
    closed = request.get("closed_date", None)
    status = request.get("status", None)
    desc = request.get("descriptor", "")
    addr = request.get("incident_address", "")
    if created:
        popup_text += "Created: {}\n".format(
            datetime.fromisoformat(created).strftime("%b %d %Y"))
    if closed:
        popup_text += "Closed: {}\n".format(
            datetime.fromisoformat(closed).strftime("%b %d %Y"))
    if status:
        popup_text += "Status: {}\n".format(status)
    if desc and addr:
        popup_text += "{} at {}".format(desc, addr.title())
    return popup_text

def main():
    requests = fetch_311_data()

    coordinates = []
    marker_layer = folium.FeatureGroup("Markers")
    for request in requests:
        try:
            lat = float(request.get("latitude", 0))
            lon = float(request.get("longitude", 0))
            if lat != 0 and lon != 0:  # Skip invalid coordinates
                coordinates.append([lat, lon])

            folium.Marker(
                location=[lat, lon],
                tooltip="Details",
                popup=get_popup_text(request)
            ).add_to(marker_layer)
        except (ValueError, TypeError):
            continue  # Skip invalid data

    map = folium.Map([40.0, -73.0], zoom_start=6)
    HeatMap(coordinates, name="Heatmap").add_to(map)
    marker_layer.add_to(map)
    folium.LayerControl().add_to(map)
    map.save('index.html')

if __name__ == "__main__":
    main()
