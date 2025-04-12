from fastapi import FastAPI, HTTPException
import requests
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
import wikipedia

app = FastAPI()

# Add this right after creating your FastAPI app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# URLs for the JSON data
DATA_URLS = [
    "https://unitedstates.github.io/congress-legislators/legislators-current.json",
    "https://unitedstates.github.io/congress-legislators/legislators-historical.json",
    "https://unitedstates.github.io/congress-legislators/executive.json",
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
    print(f"Searching for '{query}'")
    results = []

    # Search through all data sources
    for url in DATA_URLS:
        try:
            data = fetch_data(url)
            source_name = url.split("/")[-1].replace(".json", "")

            for item in data:
                # Skip if this is not a person record with a name
                if not isinstance(item, dict) or "name" not in item:
                    continue

                name = item.get("name", {})

                # Extract name components
                first = name.get("first", "").lower() if name else ""
                last = name.get("last", "").lower() if name else ""

                # Build different name formats for matching
                full_name = f"{first} {last}".lower()

                # Check for match in name
                if (query in full_name or
                    query == first or
                        query == last):

                    # Add source information
                    item["data_source"] = source_name
                    summary = wikipedia.summary(full_name)
                    item["summary"] = summary
                    results.append(item)
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

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
