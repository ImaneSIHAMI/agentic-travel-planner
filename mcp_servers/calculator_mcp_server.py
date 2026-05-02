"""
MCP Server: Calculator
Port: 3335
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, math

app = FastAPI(title="calculator-mcp")

class CalcRequest(BaseModel):
    expression: str  # e.g. "150 * 5 + 300"

@app.post("/tools/calculate")
def calculate(req: CalcRequest):
    try:
        # Safe eval using only math operations
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        result = eval(req.expression, {"__builtins__": {}}, allowed_names)
        return {
            "expression": req.expression,
            "result": result,
            "formatted": f"{result:,.2f}" if isinstance(result, float) else str(result),
        }
    except Exception as e:
        return {"error": str(e), "expression": req.expression}

@app.get("/tools")
def list_tools():
    return {
        "tools": [{
            "name": "calculate",
            "description": "Performs arithmetic operations required during agent reasoning.",
            "input_schema": {"expression": "string (e.g. '100 * 5 + 200')"},
            "endpoint": "/tools/calculate",
            "method": "POST",
        }]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3335)
