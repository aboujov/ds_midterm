# tests/test_api.py
import types
from fastapi.testclient import TestClient

from api.main import app
import api.main as api_main

API_KEY = "test-key"

def setup_module(_):
    # set the same API key the app reads
    api_main.API_KEY = API_KEY

def client():
    return TestClient(app)

# --- tiny fake cursor that supports .sort().limit() and yields data
class FakeCursor(list):
    def sort(self, *_):
        return self
    def limit(self, *_):
        return self

# -------- /health (no auth required)
def test_health_ok():
    c = client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "fastapi"

# -------- /raw (requires auth) with fake Mongo
def test_raw_requires_auth():
    c = client()
    assert c.get("/raw").status_code == 401

def test_raw_ok(monkeypatch):
    # fake get_collection().find(...).sort().limit()
    class FakeColl:
        def find(self, *_args, **_kwargs):
            return FakeCursor([
                {"url": "https://a", "ok": True, "count": 2, "titles": ["x","y"]},
                {"url": "https://b", "ok": False, "error": "timeout", "count": 0, "titles": []},
            ])
    monkeypatch.setattr(api_main, "get_collection", lambda: FakeColl())

    c = client()
    r = c.get("/raw?limit=2", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["url"].startswith("https://")

# -------- /processed (requires auth) with fake clean collection
def test_processed_ok(monkeypatch):
    class FakeClean:
        def find(self, *_args, **_kwargs):
            return FakeCursor([
                {"url": "https://hn", "domain": "news.ycombinator.com", "title": "HN", "length": 123, "preview": "Hello"},
                {"url": "https://py", "domain": "www.python.org", "title": "Python", "length": 456, "preview": "World"},
            ])
    monkeypatch.setattr(api_main, "get_clean_collection", lambda: FakeClean())

    c = client()
    r = c.get("/processed?limit=2", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    j = r.json()
    assert len(j["items"]) == 2
    assert "preview" in j["items"][0]

# -------- /search (requires auth) with fake retriever
def test_search_ok(monkeypatch):
    fake_hits = [
        {"id": "1", "distance": 0.12, "url": "https://example.com/a", "title": "A", "snippet": "aaa"},
        {"id": "2", "distance": 0.34, "url": "https://example.com/b", "title": "B", "snippet": "bbb"},
    ]
    monkeypatch.setattr(api_main, "retrieve", lambda q, k=3: fake_hits)

    c = client()
    r = c.get("/search?q=test&k=2", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    j = r.json()
    assert j["query"] == "test"
    assert len(j["results"]) == 2
    assert j["results"][0]["title"] == "A"
