# 🧳 Agentic Travel Planning Assistant
**LangChain + MCP + Ollama + Streamlit**

---

## Project Structure

```
travel_agent/
├── mcp_servers/
│   ├── destination_mcp_server.py   # Port 3331 — travel-search-mcp
│   ├── budget_mcp_server.py        # Port 3332 — finance-mcp
│   ├── weather_mcp_server.py       # Port 3333 — weather-mcp
│   ├── currency_mcp_server.py      # Port 3334 — currency-mcp
│   └── calculator_mcp_server.py    # Port 3335 — calculator-mcp
├── agent/
│   └── travel_agent.py             # LangChain ReAct agent
├── gui/
│   └── app.py                      # Streamlit GUI
├── start_servers.py                # Launch all MCP servers
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install & start Ollama
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama serve                       # keep this terminal open
```

### 4. Start all MCP servers (new terminal)
```bash
python start_servers.py
```
You should see all 5 servers respond with 🟢 OK.

### 5. Launch the Streamlit GUI (new terminal)
```bash
cd gui
streamlit run app.py
```

Or test the agent from CLI:
```bash
cd agent
python travel_agent.py
```

---

## Architecture

```
Streamlit GUI
     │
     ▼
LangChain ReAct Agent  ←── Ollama LLM (local)
     │
     ├── search_destination  →  http://localhost:3331
     ├── estimate_budget     →  http://localhost:3332
     ├── get_weather         →  http://localhost:3333
     ├── convert_currency    →  http://localhost:3334
     └── calculate           →  http://localhost:3335
```

---

## Example Queries

- `Plan a 5-day trip to Barcelona in July with a moderate budget, show costs in EUR`
- `Plan a 7-day trip to Tokyo in April with a budget travel style`
- `Plan 4 days in Paris in December, show costs in GBP`

---

## Tool Reference

| Tool | MCP Server | Port | Input Format |
|------|-----------|------|-------------|
| search_destination | travel-search-mcp | 3331 | `"Barcelona"` |
| estimate_budget | finance-mcp | 3332 | `"Barcelona, 5, moderate"` |
| get_weather | weather-mcp | 3333 | `"Barcelona, 7"` (month) |
| convert_currency | currency-mcp | 3334 | `"1500, EUR"` |
| calculate | calculator-mcp | 3335 | `"150 * 5 + 300"` |

---

## Exercises (from lab)

1. **Display each tool call in the GUI** ✅ Already implemented (expandable cards)
2. **Add a critic agent** — Add a second LLM call that reviews the plan and suggests improvements
3. **Budget constraint enforcement** — Accept a max budget and re-plan if exceeded

## Extensions

- Add memory with `ConversationBufferMemory`
- Dockerize each MCP server
- Convert to planner–executor–critic architecture
