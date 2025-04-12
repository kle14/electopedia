from fastapi import FastAPI, HTTPException
import yaml
import pathlib
from functools import lru_cache

app = FastAPI()

# Define the path to congress-legislators data
BASE_DIR = pathlib.Path(__file__).parent.parent  # Navigate to backend folder
DATA_DIR = BASE_DIR / "data" / "congress-legislators"


@lru_cache(maxsize=1)
def load_legislators_data():
    """Load legislator data from YAML files and cache it"""
    try:
        # Load current legislators
        with open(DATA_DIR / "legislators-current.yaml", "r") as f:
            current = yaml.safe_load(f)

        # Load historical legislators
        with open(DATA_DIR / "legislators-historical.yaml", "r") as f:
            historical = yaml.safe_load(f)

        # Load executives (presidents and vice presidents)
        with open(DATA_DIR / "executive.yaml", "r") as f:
            executives = yaml.safe_load(f)

        return current, historical, executives
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Data files not found. Make sure congress-legislators repository is correctly cloned at {DATA_DIR}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading data: {str(e)}")


def search_politician(query: str):
    """Search for politicians by name"""
    current, historical, executives = load_legislators_data()
    query = query.lower().replace("_", " ")
    results = []

    # Search through all sources
    all_politicians = current + historical + executives

    for politician in all_politicians:
        name = politician.get("name", {})
        first = name.get("first", "").lower()
        last = name.get("last", "").lower()
        middle = name.get("middle", "").lower()

        # Create full name for matching
        full_name = " ".join(filter(None, [first, middle, last])).lower()

        # Check for matches
        if query == first or query == last or query in full_name:
            results.append(politician)

    return results


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI with uv!"}

# Define a path parameter route that captures the query format


@app.get("/{path:path}")
def process_query(path: str):
    if path.startswith("query="):
        query = path[6:]  # Remove "query=" prefix
        try:
            results = search_politician(query)
            if not results:
                return {"message": f"No results found for '{query}'", "results": []}
            return {"results": results}
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"An error occurred: {str(e)}")
    else:
        return {"message": "Invalid path. Use /query=politician_name"}
