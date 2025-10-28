# client.py
import sys
import requests

BASE = "http://127.0.0.1:5050"

def health():
    r = requests.get(f"{BASE}/")
    r.raise_for_status()
    return r.json()

def echo(payload: dict):
    r = requests.post(f"{BASE}/echo", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    # Simple CLI:
    #   python client.py health
    #   python client.py echo '{"msg":"hi"}'
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "health").lower()
    if cmd == "health":
        print(health())
    elif cmd == "echo":
        import json
        raw = sys.argv[2] if len(sys.argv) > 2 else '{"msg":"hello"}'
        print(echo(json.loads(raw)))
    else:
        print("Usage: python client.py [health|echo '{\"msg\":\"hi\"}']")
