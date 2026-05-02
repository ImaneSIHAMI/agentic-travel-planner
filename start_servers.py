"""
start_servers.py — Launch all 5 MCP servers in background processes.
Run from the project root: python start_servers.py
"""
import subprocess, sys, time, os, signal, requests

SERVERS = [
    {"name": "Destination Search", "file": "mcp_servers/destination_mcp_server.py",  "port": 3331},
    {"name": "Budget Calculator",  "file": "mcp_servers/budget_mcp_server.py",        "port": 3332},
    {"name": "Weather Tool",       "file": "mcp_servers/weather_mcp_server.py",        "port": 3333},
    {"name": "Currency Converter", "file": "mcp_servers/currency_mcp_server.py",      "port": 3334},
    {"name": "Calculator",         "file": "mcp_servers/calculator_mcp_server.py",    "port": 3335},
]

processes = []

def start_servers():
    print("🚀 Starting MCP Tool Servers...\n")
    for srv in SERVERS:
        proc = subprocess.Popen(
            [sys.executable, srv["file"]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        processes.append(proc)
        print(f"  ✅ {srv['name']:25s} → http://localhost:{srv['port']}")
    
    print("\n⏳ Waiting for servers to start...")
    time.sleep(3)

    print("\n🔍 Health check:")
    all_ok = True
    for srv in SERVERS:
        try:
            r = requests.get(f"http://localhost:{srv['port']}/tools", timeout=3)
            status = "🟢 OK" if r.status_code == 200 else f"🔴 HTTP {r.status_code}"
        except:
            status = "🔴 Not responding"
            all_ok = False
        print(f"  {srv['name']:25s} {status}")

    if all_ok:
        print("\n✅ All servers are running!\n")
    else:
        print("\n⚠️  Some servers failed to start. Check the server files.\n")

    return all_ok

def stop_servers():
    print("\n🛑 Stopping MCP servers...")
    for proc in processes:
        proc.terminate()
    print("   All servers stopped.")

if __name__ == "__main__":
    ok = start_servers()
    if ok:
        print("Press Ctrl+C to stop all servers.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_servers()