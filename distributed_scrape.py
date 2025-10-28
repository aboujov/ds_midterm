# distributed_scrape.py
import ray
import requests
from typing import List, Dict
from scraper.parser import parse_titles_from_html

ray.init(ignore_reinit_error=True, include_dashboard=False)

@ray.remote
def fetch_and_parse(url: str, limit: int = 5) -> Dict:
    """Worker: fetch raw HTML, parse titles, return structured result."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        titles = parse_titles_from_html(r.text, limit=limit)
        return {"url": url, "ok": True, "count": len(titles), "titles": titles}
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e), "count": 0, "titles": []}

def run_distributed(urls: List[str], limit: int = 5) -> List[Dict]:
    # Launch N remote tasks in parallel
    futures = [fetch_and_parse.remote(u, limit) for u in urls]
    return ray.get(futures)

if __name__ == "__main__":
    test_urls = [
        "https://news.ycombinator.com",
        "https://www.python.org/",
        "https://www.bbc.com/",
    ]
    results = run_distributed(test_urls, limit=5)
    for item in results:
        print(item)
