"""
app.py — Streamlit GUI for the Agentic Travel Planning Assistant
Run: streamlit run app.py
"""
import streamlit as st
import sys, os, json, time, requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))

# ─────────────────────────────────────────────
# Page config & custom CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background: #0d1117; }
.stApp { background: linear-gradient(135deg, #0d1117 0%, #0f1923 100%); }

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #f0e6d3 !important;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #1a2a3a 0%, #0d1f2d 100%);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}
.hero-banner h1 {
    font-size: 2.8rem;
    color: #d4af37 !important;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-banner p {
    color: #8b9eb0;
    font-size: 1.05rem;
    margin-top: 0.5rem;
}

/* Tool call card */
.tool-card {
    background: rgba(20, 35, 50, 0.8);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-left: 3px solid #d4af37;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin: 0.5rem 0;
    font-family: 'DM Sans', monospace;
    font-size: 0.85rem;
}
.tool-name {
    color: #d4af37;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.tool-input {
    color: #8b9eb0;
    margin-top: 0.2rem;
}

/* Output card */
.output-card {
    background: rgba(20, 35, 50, 0.9);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 12px;
    padding: 2rem;
    color: #dce8f0;
    line-height: 1.8;
    font-size: 0.97rem;
    white-space: pre-wrap;
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}
.status-ok   { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.status-err  { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.status-warn { background: rgba(234,179,8,0.15);  color: #facc15; border: 1px solid rgba(234,179,8,0.3); }

/* Server status dot */
.dot-green { color: #4ade80; }
.dot-red   { color: #f87171; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1923 !important;
    border-right: 1px solid rgba(212,175,55,0.15);
}
section[data-testid="stSidebar"] * { color: #c8d8e4 !important; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #d4af37, #b8941e) !important;
    color: #0d1117 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-size: 1rem !important;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }

/* Input field */
.stTextArea textarea {
    background: #1a2a3a !important;
    border: 1px solid rgba(212,175,55,0.3) !important;
    color: #dce8f0 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #1a2a3a !important;
    border: 1px solid rgba(212,175,55,0.3) !important;
    color: #dce8f0 !important;
}

/* Divider */
hr { border-color: rgba(212,175,55,0.2) !important; }

/* Metric */
[data-testid="metric-container"] {
    background: rgba(20,35,50,0.8);
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 10px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MCP Server health check
# ─────────────────────────────────────────────
MCP_SERVERS = {
    "Destination Search": "http://localhost:3331/tools",
    "Budget Calculator":  "http://localhost:3332/tools",
    "Weather Tool":       "http://localhost:3333/tools",
    "Currency Converter": "http://localhost:3334/tools",
    "Calculator":         "http://localhost:3335/tools",
}

def check_server(url: str) -> bool:
    try:
        r = requests.get(url, timeout=2)
        return r.status_code == 200
    except:
        return False


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    model_name = st.selectbox(
        "Ollama Model",
        ["llama3.2", "llama3.1", "llama3", "mistral", "gemma2", "qwen2.5"],
        index=0,
        help="Make sure this model is pulled in Ollama"
    )
    
    st.markdown("---")
    st.markdown("### 🔌 MCP Server Status")
    
    all_ok = True
    for name, url in MCP_SERVERS.items():
        ok = check_server(url)
        if not ok:
            all_ok = False
        icon = "🟢" if ok else "🔴"
        st.markdown(f"{icon} **{name}**")
    
    if not all_ok:
        st.warning("⚠️ Some MCP servers are offline.\nRun: `python start_servers.py`")
    else:
        st.success("✅ All servers online")
    
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    
    examples = [
        "Plan a 5-day trip to Barcelona in July, moderate budget, show costs in EUR",
        "Plan a 7-day trip to Tokyo in April with a budget travel style",
        "Plan 4 days in Paris in December, show costs in GBP",
        "Plan a 10-day trip to New York in August, expensive style",
    ]
    
    selected_example = st.selectbox("Load an example:", [""] + examples)
    
    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown("""
    1. Your query → **LangChain Agent**
    2. Agent reasons with **Ollama LLM**
    3. Agent calls **MCP Tool Servers**
    4. Results synthesized into a **travel plan**
    """)


# ─────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1>✈️ AI Travel Planner</h1>
    <p>Agentic travel planning powered by LangChain · MCP · Ollama</p>
</div>
""", unsafe_allow_html=True)

# Input
default_query = selected_example if selected_example else ""
user_query = st.text_area(
    "Describe your trip",
    value=default_query,
    height=100,
    placeholder='e.g. "Plan a 5-day trip to Barcelona in July with a moderate budget, show costs in EUR"',
)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    plan_btn = st.button("🗺️ Plan My Trip", use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Agent execution
# ─────────────────────────────────────────────
if plan_btn:
    if not user_query.strip():
        st.error("Please describe your trip first.")
    else:
        # Import agent
        try:
            from travel_agent import run_travel_agent
        except ImportError as e:
            st.error(f"Could not import agent: {e}")
            st.stop()

        # Split layout: tool calls | travel plan
        col_tools, col_plan = st.columns([1, 2])

        with col_tools:
            st.markdown("### 🔧 Tool Calls")
            tool_placeholder = st.empty()

        with col_plan:
            st.markdown("### 🗺️ Travel Plan")
            plan_placeholder = st.empty()

        with st.spinner(f"🤖 Agent is planning your trip with **{model_name}**..."):
            start = time.time()
            try:
                result = run_travel_agent(user_query, model_name=model_name)
                elapsed = round(time.time() - start, 1)

                # Show tool calls
                with col_tools:
                    if result["steps"]:
                        tool_html = ""
                        for step in result["steps"]:
                            # Try to pretty-print JSON output
                            try:
                                obs = json.loads(step["output"])
                                obs_str = json.dumps(obs, indent=2)[:300] + ("…" if len(step["output"]) > 300 else "")
                            except:
                                obs_str = str(step["output"])[:300]

                            tool_html += f"""
                            <div class="tool-card">
                                <div class="tool-name">🔨 {step['tool']}</div>
                                <div class="tool-input">📥 <b>Input:</b> {step['input']}</div>
                                <details style="margin-top:0.4rem;">
                                    <summary style="color:#8b9eb0;cursor:pointer;font-size:0.8rem;">View response</summary>
                                    <pre style="color:#6b8a9e;font-size:0.75rem;margin-top:0.4rem;white-space:pre-wrap;">{obs_str}</pre>
                                </details>
                            </div>
                            """
                        tool_placeholder.markdown(tool_html, unsafe_allow_html=True)
                    else:
                        tool_placeholder.info("No tool calls recorded.")

                # Show travel plan
                with col_plan:
                    plan_placeholder.markdown(
                        f'<div class="output-card">{result["output"]}</div>',
                        unsafe_allow_html=True,
                    )

                # Metrics
                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("⏱️ Time", f"{elapsed}s")
                m2.metric("🔧 Tool Calls", len(result["steps"]))
                m3.metric("🤖 Model", model_name)

            except Exception as e:
                st.error(f"❌ Agent error: {e}")
                st.markdown("**Troubleshooting:**")
                st.markdown("""
                - Is Ollama running? → `ollama serve`
                - Is the model pulled? → `ollama pull llama3.2`
                - Are MCP servers running? → `python start_servers.py`
                """)
