"""
MCP Server: Budget Calculator
Port: 3332
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="finance-mcp")

# Estimated daily costs in USD per destination category
COST_PROFILES = {
    "expensive": {"accommodation": 180, "food": 80, "transport": 40, "activities": 60},
    "moderate": {"accommodation": 100, "food": 50, "transport": 25, "activities": 35},
    "budget": {"accommodation": 50, "food": 25, "transport": 15, "activities": 20},
}

CITY_TIERS = {
    "paris": "expensive", "london": "expensive", "new york": "expensive",
    "zurich": "expensive", "tokyo": "expensive", "amsterdam": "expensive",
    "barcelona": "moderate", "rome": "moderate", "lisbon": "moderate",
    "prague": "moderate", "istanbul": "moderate", "dubai": "moderate",
    "bangkok": "budget", "ho chi minh": "budget", "bali": "budget",
    "cairo": "budget", "marrakech": "budget",
}

class BudgetRequest(BaseModel):
    destination: str
    days: int
    travel_style: str = "moderate"  # budget, moderate, expensive

@app.post("/tools/estimate_budget")
def estimate_budget(req: BudgetRequest):
    key = req.destination.lower()
    tier = "moderate"
    for city, city_tier in CITY_TIERS.items():
        if city in key or key in city:
            tier = city_tier
            break
    # Override with user preference if provided
    if req.travel_style in COST_PROFILES:
        tier = req.travel_style

    profile = COST_PROFILES[tier]
    daily_total = sum(profile.values())
    total = daily_total * req.days
    # Add flights estimate
    flights = 600 if tier == "budget" else (900 if tier == "moderate" else 1300)

    return {
        "destination": req.destination,
        "days": req.days,
        "travel_style": tier,
        "daily_breakdown_usd": profile,
        "daily_total_usd": daily_total,
        "accommodation_total_usd": profile["accommodation"] * req.days,
        "food_total_usd": profile["food"] * req.days,
        "transport_total_usd": profile["transport"] * req.days,
        "activities_total_usd": profile["activities"] * req.days,
        "estimated_flights_usd": flights,
        "total_usd": total + flights,
        "note": f"Estimate for {req.days} days in {req.destination} ({tier} style) including flights.",
    }

@app.get("/tools")
def list_tools():
    return {
        "tools": [{
            "name": "estimate_budget",
            "description": "Estimates total travel cost based on destination and number of days.",
            "input_schema": {"destination": "string", "days": "int", "travel_style": "string (budget/moderate/expensive)"},
            "endpoint": "/tools/estimate_budget",
            "method": "POST",
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3332)
