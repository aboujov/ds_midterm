# api/main.py
import os, time
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from db import get_collection  # raw scrapes
from db_clean import get_clean_collection
from rag.retriever import retrieve

API_KEY = os.getenv("API_KEY", "dev-key")  # set your own in env for demo

app = FastAPI(title="DS Midterm API", version="1.0.0")

# ---- tiny in-memory rate limiter (per API key) ----
# simple token bucket: 30 requests / 60s default
BUCKETS = {}
RATE = int(os.getenv("RATE_LIMIT_COUNT", "30"))
WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

def check_rate_limit(key: str):
    now = int(time.time())
    win = now // WINDOW
    used, win_id = BUCKETS.get(key, (0, win))
    if win_id != win:
        used, win_id = 0, win
    if used >= RATE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    BUCKETS[key] = (used + 1, win_id)

# ---- auth dependency ----
def require_key(x_api_key: str | None):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    check_rate_limit(x_api_key)

@app.middleware("http")
async def auth_and_limit(request: Request, call_next):
    # skip health
    if request.url.path == "/health":
        return await call_next(request)
    try:
        api_key = request.headers.get("x-api-key")
        require_key(api_key)
    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)
    return await call_next(request)

@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi"}

@app.get("/raw")
def get_raw(limit: int = 10):
    """Return recent raw scraped items: url, status(ok), count, titles (truncated)."""
    coll = get_collection()
    docs = list(
        coll.find({}, {"_id": 0, "url": 1, "ok": 1, "count": 1, "titles": 1, "error": 1})
            .sort([("_id", -1)])
            .limit(max(1, min(limit, 100)))
    )
    return {"items": docs, "limit": limit}

@app.get("/processed")
def get_processed(limit: int = 10, domain: str | None = None, with_text: bool = False):
    """
    Return recent cleaned/enhanced documents from Mongo.
    - limit: 1..100
    - domain: optional filter (e.g., 'news.ycombinator.com')
    - with_text: include full_text if true, else omit to keep payload small
    """
    coll = get_clean_collection()

    proj = {
        "_id": 0,
        "url": 1,
        "domain": 1,
        "title": 1,
        "length": 1,
        "preview": 1,
        "created_at": 1,
    }
    if with_text:
        proj["full_text"] = 1

    q = {}
    if domain:
        q["domain"] = domain

    docs = list(
        coll.find(q, proj)
            .sort([("_id", -1)])
            .limit(max(1, min(limit, 100)))
    )
    return {"items": docs, "limit": limit, "domain": domain, "with_text": with_text}

@app.get("/search")
def search(q: str, k: int = 3):
    """
    Vector search over cleaned docs (Chroma index).
    - q: user query text
    - k: top-k results (default 3)
    """
    k = max(1, min(k, 10))
    hits = retrieve(q, k=k)
    return {"query": q, "k": k, "results": hits}
