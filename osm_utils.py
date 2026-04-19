import requests
import json

# Returns latitude and longitude coordinates of given address
def query_coords(address, postcode):
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": f"{address}, {postcode}",
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

    response = requests.get(overpass_url, params={"data": query})

    return response.json()

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

# Parses json data into readable text
def amenities_to_text(summary):
    return f"""
    Nearby amenities:
    - {summary['schools']} schools
    - {summary['supermarkets']} supermarkets
    - {summary['stations']} train stations
    - {summary['cafes']} cafes
    - {summary['parks']} parks
    """

# Returns sum of total nearby amenities for given address
def get_amenity_score(address, postcode):
    amenity_count = 0
    lat, lon = query_coords(address, postcode)

    overpass_data = query_overpass(lat, lon)

    for element in overpass_data.get("elements", []):
        amenity_count += 1

    return amenity_count

# Returns parsed amenity summary text for given address
def get_amenity_text(address, postcode):
    print(address, postcode)
    lat, lon = query_coords(address, postcode)

    print(lat, lon)

    try:
        overpass_data = query_overpass(lat, lon)
    except:
        overpass_data = query_overpass(lat, lon)

    summary = summarise_amenities(overpass_data)
    ammenities_text = amenities_to_text(summary)

    print(ammenities_text)

    return ammenities_text
