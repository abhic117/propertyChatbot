import requests
import json
import pandas as pd
import time
import os

PROCESSED_JSON_FILE = "postcode_amenity_data.json"

# Returns latitude and longitude coordinates of given address
def query_coords(postcode):
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": f"{int(postcode)}, NSW, Australia",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "property-ai-app"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if not data:
        return None, None

    return float(data[0]["lat"]), float(data[0]["lon"])

# Queries overpass api to return json response containing nearby amenity data
def query_overpass(lat, lon, radius=5000):
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node["amenity"="school"](around:{radius},{lat},{lon});
      node["shop"="supermarket"](around:{radius},{lat},{lon});
      node["railway"="station"](around:{radius},{lat},{lon});
      node["amenity"="cafe"](around:{radius},{lat},{lon});
      node["leisure"="park"](around:{radius},{lat},{lon});
    );
    out;
    """

    headers = {
        "User-Agent": "property-ai-app"
    }

    response = requests.get(overpass_url, params={"data": query}, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")

# Summarises json response
def summarise_amenities(data):
    summary = {
        "schools": 0,
        "supermarkets": 0,
        "stations": 0,
        "cafes": 0,
        "parks": 0
    }

    for element in data.get("elements", []):
        tags = element.get("tags", {})

        if tags.get("amenity") == "school":
            summary["schools"] += 1
        elif tags.get("shop") == "supermarket":
            summary["supermarkets"] += 1
        elif tags.get("railway") == "station":
            summary["stations"] += 1
        elif tags.get("amenity") == "cafe":
            summary["cafes"] += 1
        elif tags.get("leisure") == "park":
            summary["parks"] += 1

    return summary

def calculate_score(data):
    return data["schools"] * 0.2 + data["supermarkets"] * 0.2 + data["stations"] * 0.2 + data["cafes"] * 0.2 + data["parks"] * 0.2

# Gets the amenity data for each unique postcode in dataset and saves them to a file
def main():
    df = pd.read_parquet('processed_nsw_property_data.parquet')
    amenity_results = {}

    # Filter df and store only unique postcodes
    unique_postcodes = df['post_code'].unique().tolist()
    unique_postcodes = [x for x in unique_postcodes if x == x and x != 0]

    for index, postcode in enumerate(unique_postcodes):
        print(f"processing {index + 1} of {len(unique_postcodes)}")

        lat, lon = query_coords(postcode)
        if lon is None:
            print("Invalid, continuing...")
            continue

        time.sleep(1)

        overpass_data = query_overpass(lat, lon)

        amenity_summary = summarise_amenities(overpass_data)
        amenity_score = calculate_score(amenity_summary)

        amenity_results[postcode] = {
            "coordinates": {
                "lat": lat,
                "lon": lon,
            },
            "amenities": amenity_summary,
            "amenity_score": amenity_score
        }

        time.sleep(1)

    with open(PROCESSED_JSON_FILE, "w") as f:
        json.dump(amenity_results, f, indent=4)

if not os.path.exists(PROCESSED_JSON_FILE):
    main()
