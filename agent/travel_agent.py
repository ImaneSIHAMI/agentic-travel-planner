"""
agent/travel_agent.py

LangChain + LangGraph ReAct agent that connects to all 5 MCP servers
and plans trips autonomously using Ollama (local LLM).
Compatible with langchain >= 1.0 / langgraph >= 0.2
"""
import requests
import json
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

# ─────────────────────────────────────────────
# 1. MCP Server URLs
# ─────────────────────────────────────────────

MCP_SERVERS = {
    "destination": "http://localhost:3331",
    "budget":      "http://localhost:3332",
    "weather":     "http://localhost:3333",
    "currency":    "http://localhost:3334",
    "calculator":  "http://localhost:3335",
}

def call_mcp(server_url: str, endpoint: str, payload: dict) -> dict:
    """Generic MCP HTTP call."""
    try:
        resp = requests.post(f"{server_url}{endpoint}", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": f"MCP server at {server_url} is not running. Start it first."}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 2. Tool Definitions (using @tool decorator)
# ─────────────────────────────────────────────

@tool
def search_destination(destination: str) -> str:
    """
    Retrieves tourist attractions, landmarks, and activities for a destination.
    Use this first for any trip planning request.
    Input: destination name (e.g. 'Barcelona', 'Paris', 'Tokyo').
    """
    result = call_mcp(MCP_SERVERS["destination"], "/tools/search_destination",
                      {"destination": destination})
    return json.dumps(result, indent=2)


@tool
def estimate_budget(destination: str, days: int, travel_style: str = "moderate") -> str:
    """
    Estimates total travel cost in USD based on destination and number of days.
    travel_style must be one of: budget, moderate, expensive.
    Always call this to give the user a cost estimate.
    """
    result = call_mcp(MCP_SERVERS["budget"], "/tools/estimate_budget",
                      {"destination": destination, "days": days, "travel_style": travel_style})
    return json.dumps(result, indent=2)


@tool
def get_weather(destination: str, month: int) -> str:
    """
    Provides weather conditions and travel tips for a destination by month.
    Use this to recommend appropriate activities (outdoor vs indoor).
    month is a number from 1 (January) to 12 (December).
    """
    result = call_mcp(MCP_SERVERS["weather"], "/tools/get_weather",
                      {"destination": destination, "month": month})
    return json.dumps(result, indent=2)


@tool
def convert_currency(amount_usd: float, target_currency: str) -> str:
    """
    Converts a USD amount to another currency.
    Use this when the user mentions a non-USD currency (EUR, GBP, JPY, MAD, etc.).
    amount_usd: the amount in US dollars.
    target_currency: currency code like EUR, GBP, JPY, MAD.
    """
    result = call_mcp(MCP_SERVERS["currency"], "/tools/convert_currency",
                      {"amount_usd": amount_usd, "target_currency": target_currency})
    return json.dumps(result, indent=2)


@tool
def calculate(expression: str) -> str:
    """
    Performs arithmetic calculations.
    Use for precise cost calculations instead of estimating.
    Input: a math expression string (e.g. '150 * 5 + 300').
    """
    result = call_mcp(MCP_SERVERS["calculator"], "/tools/calculate",
                      {"expression": expression})
    return json.dumps(result, indent=2)


# ─────────────────────────────────────────────
# 3. Agent Setup
# ─────────────────────────────────────────────

TOOLS = [search_destination, estimate_budget, get_weather, convert_currency, calculate]

SYSTEM_PROMPT = """You are an expert Agentic Travel Planning Assistant.
Your job is to create comprehensive, personalized travel plans using your tools.

ALWAYS follow these steps for every trip request:
1. Call search_destination to get landmarks and activities
2. Call estimate_budget to calculate costs
3. Call get_weather with the correct month number
4. If the user wants costs in a non-USD currency, call convert_currency
5. Use calculate if you need to verify any arithmetic

Finally, synthesize everything into a detailed travel plan with:
- Day-by-day itinerary with specific activities
- Budget breakdown (daily + total)
- Weather advice and clothing recommendations
- Practical travel tips
"""

def create_agent(model_name: str = "llama3.2"):
    llm = ChatOllama(
        model=model_name,
        temperature=0.3,
        base_url="http://localhost:11434",
    )
    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
    )
    return agent


# ─────────────────────────────────────────────
# 4. Public run function
# ─────────────────────────────────────────────

def run_travel_agent(user_request: str, model_name: str = "llama3.2") -> dict:
    """
    Run the travel agent for a user request.
    Returns dict with 'output' and 'steps'.
    """
    agent = create_agent(model_name)
    result = agent.invoke({"messages": [HumanMessage(content=user_request)]})

    # Extract final answer (last AI message)
    messages = result.get("messages", [])
    output = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and msg.__class__.__name__ == "AIMessage":
            output = msg.content
            break

    # Extract tool call steps
    steps = []
    ai_tool_calls = {}
    for msg in messages:
        if msg.__class__.__name__ == "AIMessage" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                ai_tool_calls[tc["id"]] = {
                    "tool": tc["name"],
                    "input": json.dumps(tc.get("args", {})),
                }
        elif msg.__class__.__name__ == "ToolMessage":
            call_id = msg.tool_call_id
            if call_id in ai_tool_calls:
                steps.append({
                    "tool": ai_tool_calls[call_id]["tool"],
                    "input": ai_tool_calls[call_id]["input"],
                    "output": msg.content,
                })

    return {
        "output": output or "No output generated.",
        "steps": steps,
    }


# ─────────────────────────────────────────────
# CLI test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    request = "Plan a 5-day trip to Barcelona in July with a moderate budget. Show costs in EUR."
    print(f"\n🧳 Request: {request}\n{'='*60}")
    result = run_travel_agent(request)
    print("\n📋 TRAVEL PLAN:\n")
    print(result["output"])
    print(f"\n🔧 TOOL CALLS: {len(result['steps'])}")
    for step in result["steps"]:
        print(f"  [{step['tool']}] {step['input'][:80]}")