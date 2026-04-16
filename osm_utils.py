import requests
import json

def query_coords(address, postcode):
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "street": address,
        "postalcode": postcode,
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

def query_overpass(lat, lon, radius=5000):
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node
      ["amenity"="school"](around:{radius},{lat},{lon});
    );
    out;
    """

    response = requests.get(overpass_url, params={"data": query})

    return response.json()

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

def amenities_to_text(summary):
    return f"""
    Nearby amenities:
    - {summary['schools']} schools
    - {summary['supermarkets']} supermarkets
    - {summary['stations']} train stations
    - {summary['cafes']} cafes
    - {summary['parks']} parks
    """