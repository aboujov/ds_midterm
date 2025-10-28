# consumer_worker.py
import ray
import requests
from typing import Dict
from mq import consume_urls
from scraper.parser import parse_titles_from_html

# Start Ray locally (single node; can scale to multi-node later)
ray.init(ignore_reinit_error=True, include_dashboard=False)

@ray.remote
def fetch_and_parse(url: str, limit: int = 5) -> Dict:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        titles = parse_titles_from_html(r.text, limit=limit)
        return {"url": url, "ok": True, "count": len(titles), "titles": titles}
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e), "count": 0, "titles": []}

def handle_url(url: str):
    # Launch a remote task per URL from the MQ
    future = fetch_and_parse.remote(url, limit=5)
    result = ray.get(future)
    print("✅ Result:", result)

if __name__ == "__main__":
    print("👷 Consumer started. Waiting for URLs in queue 'urls'...")
    consume_urls(handle_url)
