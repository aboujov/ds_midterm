from flask import Flask, jsonify, request
from scraper.scraper import scrape_titles

app = Flask(__name__)

@app.get("/")
def health():
    return jsonify(status="ok", service="server", message="Hello, Distributed Systems!")

@app.post("/echo")
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify(received=data, ok=True), 200

@app.get("/scrape")  # <-- new route
def scrape():
    url = request.args.get("url", "https://news.ycombinator.com")
    limit = int(request.args.get("limit", 10))
    result = scrape_titles(url, limit=limit)
    return jsonify(result), 200

if __name__ == "__main__":
    # 0.0.0.0 so it’s reachable from containers later
    app.run(host="0.0.0.0", port=5050)
