"""
MCP Server: Currency Converter
Port: 3334
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="currency-mcp")

# Exchange rates relative to USD (approximate, static for lab)
RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.5,
    "CAD": 1.36,
    "AUD": 1.53,
    "CHF": 0.90,
    "CNY": 7.24,
    "MAD": 10.05,   # Moroccan Dirham
    "TRY": 32.0,
    "AED": 3.67,
    "SGD": 1.34,
    "MXN": 17.2,
    "BRL": 4.97,
    "INR": 83.1,
    "THB": 35.1,
}

class CurrencyRequest(BaseModel):
    amount_usd: float
    target_currency: str  # e.g., "EUR", "GBP"

@app.post("/tools/convert_currency")
def convert_currency(req: CurrencyRequest):
    target = req.target_currency.upper().strip()
    if target not in RATES:
        return {
            "error": f"Currency '{target}' not found.",
            "available_currencies": list(RATES.keys()),
        }
    rate = RATES[target]
    converted = round(req.amount_usd * rate, 2)
    return {
        "original_amount_usd": req.amount_usd,
        "target_currency": target,
        "exchange_rate": rate,
        "converted_amount": converted,
        "formatted": f"{converted:,.2f} {target}",
        "note": "Rates are approximate and for educational purposes only.",
    }

@app.get("/tools")
def list_tools():
    return {
        "tools": [{
            "name": "convert_currency",
            "description": "Converts travel cost estimates from USD to user's preferred currency.",
            "input_schema": {"amount_usd": "float", "target_currency": "string (e.g. EUR, GBP, JPY)"},
            "endpoint": "/tools/convert_currency",
            "method": "POST",
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3334)
