# scraper/parser.py
from bs4 import BeautifulSoup

def parse_titles_from_html(html: str, limit: int = 10) -> list[str]:
    """
    Parse article titles from a raw HTML string.
    - HN: uses 'span.titleline a'
    - Fallback: <h1>/<h2>/<h3> headings
    """
    soup = BeautifulSoup(html, "html.parser")
    titles: list[str] = []

    # HN-style
    for a in soup.select("span.titleline a"):
        titles.append(a.get_text(strip=True))
        if len(titles) >= limit:
            return titles

    # Fallback headings
    for tag in soup.find_all(["h1", "h2", "h3"]):
        titles.append(tag.get_text(strip=True))
        if len(titles) >= limit:
            break

    return titles
