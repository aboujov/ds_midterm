# tests/test_scrape.py
from app.server import app
import scraper.scraper as scr

def test_scrape_route(monkeypatch):
    # Fake HTML that matches Hacker News structure
    sample_html = """
    <html><body>
      <span class="titleline"><a href="u1">Title 1</a></span>
      <span class="titleline"><a href="u2">Title 2</a></span>
      <span class="titleline"><a href="u3">Title 3</a></span>
    </body></html>
    """

    class DummyResp:
        def __init__(self, text, status_code=200):
            self.text = text
            self.status_code = status_code
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("HTTP error")

    # Monkeypatch requests.get used inside scraper.scraper
    def fake_get(url, timeout=10):
        return DummyResp(sample_html, 200)

    monkeypatch.setattr(scr.requests, "get", fake_get)

    client = app.test_client()
    res = client.get("/scrape?url=https://news.ycombinator.com&limit=2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 2
    assert data["titles"] == ["Title 1", "Title 2"]
