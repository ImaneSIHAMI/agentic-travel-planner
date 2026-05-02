"""
MCP Server: Weather Tool
Port: 3333
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="weather-mcp")

WEATHER_DATA = {
    "barcelona": {
        "spring": {"temp_c": 18, "condition": "Sunny with occasional clouds", "rain_days": 4, "tip": "Perfect for outdoor sightseeing"},
        "summer": {"temp_c": 28, "condition": "Hot and sunny", "rain_days": 1, "tip": "Visit beaches early morning; afternoons very hot"},
        "autumn": {"temp_c": 20, "condition": "Warm and mild", "rain_days": 6, "tip": "Great for walking tours and outdoor dining"},
        "winter": {"temp_c": 12, "condition": "Cool and partly cloudy", "rain_days": 5, "tip": "Less crowded; ideal for museums"},
    },
    "paris": {
        "spring": {"temp_c": 14, "condition": "Mild with some showers", "rain_days": 8, "tip": "Bring a light jacket and umbrella"},
        "summer": {"temp_c": 25, "condition": "Warm and sunny", "rain_days": 4, "tip": "Busy season; book attractions in advance"},
        "autumn": {"temp_c": 13, "condition": "Cool and rainy", "rain_days": 10, "tip": "Great for café culture and indoor museums"},
        "winter": {"temp_c": 5, "condition": "Cold and grey", "rain_days": 9, "tip": "Christmas markets are magical"},
    },
    "tokyo": {
        "spring": {"temp_c": 15, "condition": "Cherry blossoms, mild", "rain_days": 5, "tip": "Peak cherry blossom season in late March"},
        "summer": {"temp_c": 30, "condition": "Hot and humid", "rain_days": 12, "tip": "Stay hydrated; indoor activities in peak heat"},
        "autumn": {"temp_c": 18, "condition": "Crisp and clear", "rain_days": 6, "tip": "Beautiful fall foliage; excellent weather"},
        "winter": {"temp_c": 8, "condition": "Cool and dry", "rain_days": 3, "tip": "Clear skies; great views of Mt. Fuji"},
    },
}

MONTH_TO_SEASON = {
    1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn",
    11: "autumn", 12: "winter"
}

class WeatherRequest(BaseModel):
    destination: str
    month: int = 6  # 1-12

@app.post("/tools/get_weather")
def get_weather(req: WeatherRequest):
    key = req.destination.lower()
    season = MONTH_TO_SEASON.get(req.month, "summer")
    
    for city, seasons in WEATHER_DATA.items():
        if city in key or key in city:
            weather = seasons[season]
            return {
                "destination": req.destination,
                "month": req.month,
                "season": season,
                "average_temp_celsius": weather["temp_c"],
                "average_temp_fahrenheit": round(weather["temp_c"] * 9/5 + 32, 1),
                "condition": weather["condition"],
                "rainy_days_per_month": weather["rain_days"],
                "travel_tip": weather["tip"],
                "recommended_clothing": "Light clothes & sunscreen" if weather["temp_c"] > 22 else (
                    "Layers and light jacket" if weather["temp_c"] > 12 else "Warm coat and layers"
                ),
                "outdoor_friendly": weather["rain_days"] < 7,
            }

    # Generic fallback
    return {
        "destination": req.destination,
        "month": req.month,
        "season": season,
        "average_temp_celsius": 20,
        "condition": "Variable — check local forecasts",
        "travel_tip": "Pack layers to be safe.",
        "outdoor_friendly": True,
    }

@app.get("/tools")
def list_tools():
    return {
        "tools": [{
            "name": "get_weather",
            "description": "Provides weather conditions for the destination by month to help plan activities.",
            "input_schema": {"destination": "string", "month": "int (1-12)"},
            "endpoint": "/tools/get_weather",
            "method": "POST",
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3333)
