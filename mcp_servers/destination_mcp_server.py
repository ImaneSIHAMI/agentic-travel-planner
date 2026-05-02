"""
MCP Server: Destination Search
Port: 3331
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, json

app = FastAPI(title="travel-search-mcp")

DESTINATIONS = {
    "barcelona": {
        "landmarks": ["Sagrada Família", "Park Güell", "Casa Batlló", "La Rambla", "Gothic Quarter"],
        "activities": ["Beach at Barceloneta", "Tapas tour", "Flamenco show", "FC Barcelona museum", "Picasso Museum"],
        "best_areas": ["Eixample", "El Born", "Gràcia", "Barceloneta"],
    },
    "paris": {
        "landmarks": ["Eiffel Tower", "Louvre", "Notre-Dame", "Musée d'Orsay", "Sacré-Cœur"],
        "activities": ["Seine river cruise", "Montmartre walk", "Wine tasting", "Versailles day trip", "French cooking class"],
        "best_areas": ["Le Marais", "Saint-Germain", "Montmartre", "Champs-Élysées"],
    },
    "tokyo": {
        "landmarks": ["Senso-ji Temple", "Tokyo Skytree", "Meiji Shrine", "Shibuya Crossing", "Shinjuku Gyoen"],
        "activities": ["Sushi making class", "Akihabara electronics tour", "Sumo tournament", "Tea ceremony", "Mount Fuji day trip"],
        "best_areas": ["Shinjuku", "Shibuya", "Asakusa", "Ginza"],
    },
    "new york": {
        "landmarks": ["Statue of Liberty", "Central Park", "Times Square", "Brooklyn Bridge", "Empire State Building"],
        "activities": ["Broadway show", "Food tour", "Museum hopping", "Bike Central Park", "Rooftop bar crawl"],
        "best_areas": ["Manhattan", "Brooklyn", "Queens", "Williamsburg"],
    },
}

class DestinationRequest(BaseModel):
    destination: str

@app.post("/tools/search_destination")
def search_destination(req: DestinationRequest):
    key = req.destination.lower()
    for name, data in DESTINATIONS.items():
        if name in key or key in name:
            return {
                "destination": name.title(),
                "landmarks": data["landmarks"],
                "activities": data["activities"],
                "best_areas": data["best_areas"],
                "tip": f"Best time to visit {name.title()} is spring or early autumn.",
            }
    return {
        "destination": req.destination,
        "landmarks": ["Historic city center", "Local museum", "Main cathedral", "Central market"],
        "activities": ["City walking tour", "Local cuisine tasting", "Cultural site visits"],
        "best_areas": ["City center", "Old town"],
        "tip": "Research local customs before visiting.",
    }

@app.get("/tools")
def list_tools():
    return {
        "tools": [{
            "name": "search_destination",
            "description": "Retrieves tourist attractions, landmarks, and activities for a given destination.",
            "input_schema": {"destination": "string"},
            "endpoint": "/tools/search_destination",
            "method": "POST",
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3331)
