from fastapi import FastAPI, HTTPException
import requests
from functools import lru_cache

app = FastAPI()

# URLs for the JSON data
DATA_URLS = [
    "https://unitedstates.github.io/congress-legislators/legislators-current.json",
    "https://unitedstates.github.io/congress-legislators/legislators-historical.json",
    "https://unitedstates.github.io/congress-legislators/executive.json",
    "https://unitedstates.github.io/congress-legislators/legislators-social-media.json",
    "https://unitedstates.github.io/congress-legislators/committees-current.json",
    "https://unitedstates.github.io/congress-legislators/committee-membership-current.json",
    "https://unitedstates.github.io/congress-legislators/committees-historical.json",
    "https://unitedstates.github.io/congress-legislators/legislators-district-offices.json"
]


@lru_cache(maxsize=len(DATA_URLS))
def fetch_data(url):
    """Fetch and cache JSON data from a URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching data from {url}: {str(e)}")


def search_politician(query):
    """Search for a politician across all data sources"""
    query = query.lower().replace("_", " ").strip()
    results = []

    # Search through all data sources
    for url in DATA_URLS:
        data = fetch_data(url)
        source_name = url.split("/")[-1].replace(".json", "")

        for item in data:
            # Skip if this is not a person record
            if not isinstance(item, dict) or "name" not in item:
                continue

            name = item.get("name", {})

            # Extract name components
            first = name.get("first", "").lower() if name else ""
            last = name.get("last", "").lower() if name else ""
            middle = name.get("middle", "").lower() if name else ""

            # Build different name formats for matching
            full_name = f"{first} {last}".lower()
            full_name_with_middle = f"{first} {middle} {last}".lower().strip()

            # Check for match in name
            if (query in full_name or
                query in full_name_with_middle or
                query == first or
                    query == last):

                # Add source information
                item["data_source"] = source_name
                results.append(item)

    return results

@app.get("/query={politician_name}")
async def get_politician(politician_name: str):
    try:
        results = search_politician(politician_name)

        if not results:
            return {"message": f"No data found for '{politician_name}'", "count": 0, "results": []}

        return {
            "message": f"Found {len(results)} results for '{politician_name}'",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
