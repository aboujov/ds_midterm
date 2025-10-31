# processing/benchmark.py
import time, requests
from typing import List, Dict
from processing.cleaner import clean_html_to_text
from processing.normalize import normalize_raw_item
from db_clean import save_clean_doc

URLS = [
    "https://news.ycombinator.com/",
    "https://www.python.org/",
    "https://www.bbc.com/",
]

def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.text

def run_benchmark(urls: List[str]) -> Dict:
    results = []
    t0_all = time.perf_counter()

    for url in urls:
        entry = {"url": url}
        t0 = time.perf_counter()
        html = fetch_html(url)
        t_fetch = time.perf_counter() - t0

        t1 = time.perf_counter()
        text = clean_html_to_text(html)
        t_clean = time.perf_counter() - t1

        t2 = time.perf_counter()
        doc = normalize_raw_item({"url": url, "html": html})
        t_norm = time.perf_counter() - t2

        # store cleaned doc (for indexing proof)
        try:
            _id = save_clean_doc(doc)
        except Exception as e:
            _id = f"save_failed: {e}"

        entry.update({
            "fetch_s": round(t_fetch, 4),
            "clean_s": round(t_clean, 4),
            "normalize_s": round(t_norm, 4),
            "length": len(text),
            "stored_id": _id,
        })
        results.append(entry)

    total = time.perf_counter() - t0_all
    return {"total_s": round(total, 4), "items": results}

if __name__ == "__main__":
    out = run_benchmark(URLS)
    print("Total time (s):", out["total_s"])
    for it in out["items"]:
        print(f"- {it['url']}")
        print(f"  fetch={it['fetch_s']}s clean={it['clean_s']}s normalize={it['normalize_s']}s length={it['length']}")
        print(f"  stored_id={it['stored_id']}")
